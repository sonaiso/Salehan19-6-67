"""Tests for Phase 5.1 Industrial Hardening (14 fixes)."""
from __future__ import annotations

import pytest
from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases
from mcd.industrial.industrial_test_runner import (
    IndustrialTestRunner,
    IndustrialResult,
    _evaluate_pass,
    _derive_certainty_policy,
    _derive_evidence_status,
    _collect_warnings,
    _CERTAINTY_ALIASES,
)
from mcd.industrial.source_trust_policy import SourceTrustPolicy, SourceTrustResult
from mcd.industrial.pilot_readiness import (
    PilotReadinessGate,
    PilotReadinessCriteria,
    PilotReadinessResult,
    check_schema_stability,
)
from mcd.industrial.latency_benchmark import LatencyBenchmark, percentile
from mcd.industrial.forbidden_behavior_detector import ForbiddenBehaviorDetector, ForbiddenBehaviorMatch
from mcd.industrial.industrial_report import generate_industrial_report_from_results
from mcd.industrial.serializers import pilot_readiness_to_dict
from mcd.industrial.api_contract import SourceDocument, SourceAPIResponse, SourceQuery


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _ok_response(docs_content: list[str] = None, warnings: list[str] = None) -> SourceAPIResponse:
    docs = []
    for i, c in enumerate(docs_content or ["محتوى الوثيقة"]):
        docs.append(SourceDocument(
            source_id=f"d{i}", title="Title", content=c,
            authority_level="official", freshness="current"
        ))
    return SourceAPIResponse(
        query_id="q1", status="ok", documents=docs,
        latency_ms=50, warnings=list(warnings or [])
    )


def _empty_response() -> SourceAPIResponse:
    return SourceAPIResponse(query_id="q1", status="empty", documents=[], latency_ms=10)


def _trust_results(n: int = 1, injection_risk: float = 0.0, warnings: list[str] = None) -> list[SourceTrustResult]:
    return [SourceTrustResult(
        source_id=f"d{i}", trust_score=0.8, authority_score=1.0, freshness_score=1.0,
        relevance_score=0.7, injection_risk=injection_risk,
        final_trust=0.8, warnings=list(warnings or [])
    ) for i in range(n)]


def _case(expected_behavior="suspend", expected_minimum_warnings=None, expected_certainty_policy="", forbidden_behaviors=None) -> IndustrialTestCase:
    return IndustrialTestCase(
        case_id="TEST-001",
        input_text="اختبار",
        source_api_scenario="empty",
        expected_behavior=expected_behavior,
        expected_minimum_warnings=expected_minimum_warnings or [],
        expected_certainty_policy=expected_certainty_policy,
        forbidden_behaviors=forbidden_behaviors or [],
    )


# ─── Fix 8: percentile() nearest-rank ─────────────────────────────────────────

def test_percentile_p95_not_max():
    values = list(range(1, 21))  # [1..20]
    assert percentile(values, 95) == 19  # nearest-rank: ceil(0.95*20)-1 = 18th idx → value 19

def test_percentile_p50_median():
    values = list(range(1, 11))  # [1..10]
    assert percentile(values, 50) == 5  # ceil(0.5*10)-1 = 4th idx → value 5

def test_percentile_empty():
    assert percentile([], 95) == 0.0

def test_percentile_single():
    assert percentile([42], 95) == 42

def test_percentile_p100():
    assert percentile([1, 2, 3, 4, 5], 100) == 5

def test_latency_benchmark_uses_percentile():
    cases = get_default_test_cases()[:5]
    bench = LatencyBenchmark()
    result = bench.run(cases)
    assert result.p95_latency_ms >= result.p50_latency_ms
    assert result.p95_latency_ms <= result.max_latency_ms


# ─── Fix 9: _compute_relevance() ──────────────────────────────────────────────

def test_relevance_high_overlap():
    policy = SourceTrustPolicy()
    doc = SourceDocument(
        source_id="d1", title="T", content="الذكاء الاصطناعي في العالم العربي",
        authority_level="official", freshness="current"
    )
    result = policy.evaluate(doc, query_text="الذكاء الاصطناعي")
    assert result.relevance_score > 0.5

def test_relevance_no_overlap_gets_base():
    policy = SourceTrustPolicy()
    doc = SourceDocument(
        source_id="d1", title="T", content="محتوى بلا صلة بالسؤال",
        authority_level="official", freshness="current"
    )
    result = policy.evaluate(doc, query_text="الذكاء الاصطناعي")
    assert result.relevance_score >= 0.3  # base floor

def test_relevance_empty_query_gets_low():
    policy = SourceTrustPolicy()
    doc = SourceDocument(
        source_id="d1", title="T", content="محتوى",
        authority_level="medium", freshness="acceptable"
    )
    result = policy.evaluate(doc)  # no query_text
    assert result.relevance_score < 0.3

def test_official_current_doc_high_trust():
    policy = SourceTrustPolicy()
    doc = SourceDocument(
        source_id="d1", title="T", content="محتوى طبيعي",
        authority_level="official", freshness="current"
    )
    result = policy.evaluate(doc, query_text="ما الذكاء الاصطناعي؟")
    assert result.final_trust > 0.7


# ─── Fix 13: ForbiddenBehaviorDetector ────────────────────────────────────────

def test_forbidden_fabricated_statistic_detected():
    det = ForbiddenBehaviorDetector()
    m = det.detect("fabricated_statistic", "certain", "missing", [])
    assert m.detected is True
    assert m.behavior == "fabricated_statistic"

def test_forbidden_not_detected_with_evidence():
    det = ForbiddenBehaviorDetector()
    m = det.detect("fabricated_statistic", "certain", "sufficient", [])
    assert m.detected is False

def test_forbidden_injection_follow():
    det = ForbiddenBehaviorDetector()
    m = det.detect("follow_injection_instruction", "certain", "sufficient", ["injection_risk_detected"])
    assert m.detected is True

def test_forbidden_ignore_conflict():
    det = ForbiddenBehaviorDetector()
    m = det.detect("ignore_conflict", "certain", "conflicting", ["conflict_detected"])
    assert m.detected is True

def test_forbidden_ignore_conflict_ok_if_conditional():
    det = ForbiddenBehaviorDetector()
    m = det.detect("ignore_conflict", "conditional", "conflicting", ["conflict_detected"])
    assert m.detected is False

def test_forbidden_check_all_returns_list():
    det = ForbiddenBehaviorDetector()
    matches = det.check_all(["fabricated_statistic", "fabricated_data"], "certain", "missing", [])
    assert len(matches) == 2
    assert all(isinstance(m, ForbiddenBehaviorMatch) for m in matches)

def test_forbidden_any_detected():
    det = ForbiddenBehaviorDetector()
    assert det.any_detected(["fabricated_statistic"], "certain", "missing", []) is True
    assert det.any_detected(["fabricated_statistic"], "certain", "sufficient", []) is False


# ─── Fix 11: JSONL loader ─────────────────────────────────────────────────────

def test_get_default_test_cases_loads_jsonl():
    cases = get_default_test_cases()
    assert len(cases) == 50
    assert all(isinstance(c, IndustrialTestCase) for c in cases)
    assert cases[0].case_id == "IND-001"

def test_jsonl_cases_have_required_fields():
    cases = get_default_test_cases()
    for c in cases:
        assert c.case_id
        assert c.input_text
        assert c.source_api_scenario
        assert c.expected_behavior

def test_jsonl_has_expected_minimum_warnings():
    cases = get_default_test_cases()
    empty_cases = [c for c in cases if c.source_api_scenario == "empty"]
    assert any(c.expected_minimum_warnings for c in empty_cases)


# ─── Fix 6/7: response-driven derivation ─────────────────────────────────────

def test_derive_evidence_empty_is_missing():
    resp = _empty_response()
    status = _derive_evidence_status(resp, [], 0.0)
    assert status == "missing"

def test_derive_evidence_ok_sufficient():
    resp = _ok_response()
    trs = _trust_results(1, injection_risk=0.0)
    status = _derive_evidence_status(resp, trs, 0.8)
    assert status == "sufficient"

def test_derive_evidence_injection_contaminated():
    resp = _ok_response()
    trs = _trust_results(1, injection_risk=0.9)
    status = _derive_evidence_status(resp, trs, 0.8)
    assert status == "contaminated"

def test_derive_certainty_empty_insufficient():
    resp = _empty_response()
    policy = _derive_certainty_policy(resp, [], 0.0, "unknown")
    assert policy == "insufficient_evidence"

def test_derive_certainty_ok_high_trust_certain():
    resp = _ok_response()
    trs = _trust_results(1)
    policy = _derive_certainty_policy(resp, trs, 0.8, "unknown")
    assert policy == "certain"

def test_derive_certainty_conflict_conditional():
    resp = _ok_response(warnings=["conflicting_evidence_detected"])
    trs = _trust_results(1)
    policy = _derive_certainty_policy(resp, trs, 0.8, "unknown")
    assert policy == "conditional"

def test_derive_certainty_injection_suspend():
    resp = _ok_response()
    trs = _trust_results(1, injection_risk=0.9)
    policy = _derive_certainty_policy(resp, trs, 0.8, "unknown")
    assert policy == "suspend"

def test_collect_warnings_empty_has_source_required():
    resp = _empty_response()
    warnings = _collect_warnings(resp, [])
    assert "source_required" in warnings

def test_collect_warnings_ok_includes_trust_warns():
    resp = _ok_response()
    trs = _trust_results(1, warnings=["stale_document"])
    warnings = _collect_warnings(resp, trs)
    assert "stale_document" in warnings


# ─── Fix 4: expected_minimum_warnings post-check ─────────────────────────────

def test_pass_fails_if_expected_warning_missing():
    case = _case(expected_behavior="suspend", expected_minimum_warnings=["source_required"])
    passed, explanation = _evaluate_pass(case, "insufficient_evidence", "missing", [], False)
    assert not passed
    assert "source_required" in explanation

def test_pass_ok_if_expected_warning_present():
    case = _case(expected_behavior="suspend", expected_minimum_warnings=["source_required"])
    passed, explanation = _evaluate_pass(
        case, "insufficient_evidence", "missing", ["source_required"], False
    )
    assert passed

def test_pass_warning_post_check_only_when_base_passes():
    case = _case(expected_behavior="detect_injection", expected_minimum_warnings=["source_required"])
    # base fails because no injection in warnings; source_required post-check should not be reached
    passed, explanation = _evaluate_pass(case, "insufficient_evidence", "missing", [], False)
    assert not passed
    assert "injection" in explanation


# ─── Fix 5: _CERTAINTY_ALIASES and post-check ─────────────────────────────────

def test_certainty_aliases_defined():
    assert "insufficient_evidence" in _CERTAINTY_ALIASES
    assert "suspend" in _CERTAINTY_ALIASES["insufficient_evidence"]
    assert "certain" in _CERTAINTY_ALIASES
    assert "strong_knowledge" in _CERTAINTY_ALIASES["certain"]

def test_certainty_alias_passes_with_suspend():
    case = _case(expected_behavior="suspend", expected_certainty_policy="insufficient_evidence")
    passed, _ = _evaluate_pass(case, "suspend", "missing", ["source_required"], False)
    assert passed

def test_certainty_post_check_fails_wrong_policy():
    case = _case(expected_behavior="suspend", expected_certainty_policy="certain")
    passed, explanation = _evaluate_pass(
        case, "insufficient_evidence", "missing", ["source_required"], False
    )
    assert not passed
    assert "certain" in explanation


# ─── Fix 3: PilotReadinessResult.status ──────────────────────────────────────

def test_evaluate_not_ready_has_status():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=False,
        industrial_test_pass_rate=0.5,
        false_certainty_rate=0.5,
        rest_api_implemented=False,
    )
    result = gate.evaluate(criteria)
    assert result.status == "not_ready"
    assert result.ready_for_pilot is False

def test_evaluate_conditional_candidate_status():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=True,
        industrial_test_pass_rate=0.95,
        false_certainty_rate=0.01,
        source_required_detection=0.95,
        injection_detection=0.95,
        json_schema_stability=0.98,
        readiness_report_exists=True,
        api_contract_defined=True,
        rest_api_implemented=False,
    )
    result = gate.evaluate(criteria)
    assert result.status == "conditional_candidate"
    assert result.ready_for_pilot is False

def test_evaluate_ready_for_pilot_status():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=True,
        industrial_test_pass_rate=0.95,
        false_certainty_rate=0.01,
        source_required_detection=0.95,
        injection_detection=0.95,
        json_schema_stability=0.98,
        readiness_report_exists=True,
        api_contract_defined=True,
        rest_api_implemented=True,
    )
    result = gate.evaluate(criteria)
    assert result.status == "ready_for_pilot"
    assert result.ready_for_pilot is True


# ─── Fix 2: no hard-coded values in evaluate_from_runner ─────────────────────

def test_evaluate_from_runner_tests_pass_false_by_default():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert "tests_pass" in result.failed_criteria

def test_evaluate_from_runner_readiness_report_false_by_default():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert "readiness_report_exists" in result.failed_criteria

def test_evaluate_from_runner_rest_api_still_absent():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert "rest_api_implemented" in result.failed_criteria


# ─── Fix 12: check_schema_stability ──────────────────────────────────────────

def test_check_schema_stability_uniform():
    dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    score = check_schema_stability({"results": dicts})
    assert score == 1.0

def test_check_schema_stability_mixed():
    dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5}]
    score = check_schema_stability({"results": dicts})
    assert 0 < score < 1.0

def test_check_schema_stability_empty():
    assert check_schema_stability({"results": []}) == 0.0

def test_serializer_has_status():
    gate = PilotReadinessGate()
    result = gate.evaluate(PilotReadinessCriteria())
    d = pilot_readiness_to_dict(result)
    assert "status" in d
    assert d["status"] in ("not_ready", "conditional_candidate", "ready_for_pilot")


# ─── Fix 1: generate_industrial_report_from_results ──────────────────────────

def test_generate_report_from_results_no_rerun():
    cases = get_default_test_cases()[:5]
    runner = IndustrialTestRunner()
    results = runner.run_all(cases)
    summary = runner.summary(results)
    report = generate_industrial_report_from_results(
        profile="test", cases=cases, results=results, summary=summary
    )
    assert "Industrial Testing Report" in report
    assert "Executive Summary" in report
    assert "test" in report

def test_generate_report_includes_all_sections():
    cases = get_default_test_cases()[:3]
    runner = IndustrialTestRunner()
    results = runner.run_all(cases)
    summary = runner.summary(results)
    report = generate_industrial_report_from_results(
        profile="default", cases=cases, results=results, summary=summary
    )
    for section in ["Source API Scenarios", "Industrial Test Results", "Pilot Readiness Gate"]:
        assert section in report


# ─── Fix 10: generate_industrial_report no duplicate runner ──────────────────

def test_industrial_report_has_no_double_execution():
    from mcd.industrial.industrial_report import generate_industrial_report
    report = generate_industrial_report(profile="quick")
    assert "Industrial Testing Report" in report


# ─── Integration: full run on JSONL cases ────────────────────────────────────

def test_run_all_returns_50_results():
    runner = IndustrialTestRunner()
    results = runner.run_all()
    assert len(results) == 50

def test_empty_scenario_gets_source_required_warning():
    runner = IndustrialTestRunner()
    cases = [c for c in get_default_test_cases() if c.source_api_scenario == "empty"]
    results = runner.run_all(cases)
    for r in results:
        assert "source_required" in r.warnings

def test_injection_scenario_gets_injection_warning():
    runner = IndustrialTestRunner()
    cases = [c for c in get_default_test_cases() if c.source_api_scenario == "injection_contaminated_doc"]
    results = runner.run_all(cases)
    for r in results:
        assert any("injection" in w for w in r.warnings)
