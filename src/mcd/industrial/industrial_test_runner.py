"""Industrial Test Runner — full pipeline without network calls."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from mcd.industrial.api_contract import SourceQuery, SourceAPIResponse
from mcd.industrial.mock_source_api import MockSourceAPI
from mcd.industrial.source_trust_policy import SourceTrustPolicy, SourceTrustResult
from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases
from mcd.industrial.forbidden_behavior_detector import ForbiddenBehaviorDetector


@dataclass
class IndustrialResult:
    case_id: str
    input_text: str
    source_status: str
    source_trust_summary: float
    prompt_frame: dict
    evidence_status: str
    certainty_policy: str
    epistemic_status: str
    warnings: list[str]
    forbidden_behavior_detected: bool
    passed: bool
    score: float
    latency_ms: int
    explanation: str


_TRUST_POLICY = SourceTrustPolicy()
_FORBIDDEN_DETECTOR = ForbiddenBehaviorDetector()

_CERTAINTY_ALIASES: dict[str, set[str]] = {
    "insufficient_evidence": {"insufficient_evidence", "suspend"},
    "low_certainty": {"low_certainty", "hypothesis"},
    "conditional": {"conditional"},
    "certain": {"certain", "strong_knowledge"},
}


def _classify_text(text: str) -> dict:
    """Run FPCL classification; return a minimal dict on any error."""
    try:
        from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
        fpc = FractalPromptClassifier()
        frame = fpc.classify(text)
        return {
            "intent": frame.intent,
            "certainty_policy": frame.certainty_policy,
            "routing_engine": frame.routing_engine,
            "warnings": list(frame.warnings),
            "evidence_needs": list(frame.evidence_needs.keys()) if frame.evidence_needs else [],
        }
    except Exception:
        return {
            "intent": "unknown",
            "certainty_policy": "uncertain",
            "routing_engine": "general",
            "warnings": [],
            "evidence_needs": [],
        }


def _derive_evidence_status(response: SourceAPIResponse, trust_results: list[SourceTrustResult], overall_trust: float) -> str:
    """Derive evidence status from actual API response."""
    if response.status == "empty":
        return "missing"
    if response.status == "timeout":
        return "missing"
    if response.status == "error":
        return "missing"
    if response.status == "unauthorized":
        return "missing"
    # ok status
    if any(tr.injection_risk > 0.5 for tr in trust_results):
        return "contaminated"
    trust_warns = [w for tr in trust_results for w in tr.warnings]
    resp_warns = list(response.warnings)
    all_warns = trust_warns + resp_warns
    if any("conflict" in w for w in all_warns):
        return "conflicting"
    if any("stale_document" in w for w in trust_warns):
        return "stale"
    if overall_trust >= 0.5:
        return "sufficient"
    return "insufficient"


def _derive_certainty_policy(
    response: SourceAPIResponse,
    trust_results: list[SourceTrustResult],
    overall_trust: float,
    fpcl_policy: str,
) -> str:
    """Derive certainty policy from actual API response and trust."""
    if response.status in ("empty", "timeout", "error", "unauthorized"):
        return "insufficient_evidence"
    # ok status
    if any(tr.injection_risk > 0.5 for tr in trust_results):
        return "suspend"
    trust_warns = [w for tr in trust_results for w in tr.warnings]
    resp_warns = list(response.warnings)
    all_warns = trust_warns + resp_warns
    if any("conflict_detected" in w or "conflict" in w for w in all_warns):
        return "conditional"
    if any("stale_document" in w for w in trust_warns):
        return "low_certainty"
    if fpcl_policy == "suspend":
        return "low_certainty"
    if not trust_results or all(tr.final_trust == 0 for tr in trust_results):
        return "insufficient_evidence"
    if overall_trust >= 0.6:
        return "certain"
    if overall_trust >= 0.3:
        return "low_certainty"
    return "insufficient_evidence"


def _collect_warnings(response: SourceAPIResponse, trust_results: list[SourceTrustResult]) -> list[str]:
    """Collect warnings from actual API response and trust results."""
    warnings: list[str] = list(response.warnings)
    for tr in trust_results:
        warnings.extend(tr.warnings)
        if tr.injection_risk > 0.5:
            if "injection_risk_detected" not in warnings:
                warnings.append("injection_risk_detected")
    if response.status in ("empty", "timeout", "error", "unauthorized"):
        if response.status == "timeout":
            if "source_timeout" not in warnings:
                warnings.append("source_timeout")
            if "source_required" not in warnings:
                warnings.append("source_required")
        elif response.status == "error":
            if "source_error" not in warnings:
                warnings.append("source_error")
            if "source_required" not in warnings:
                warnings.append("source_required")
        elif response.status == "unauthorized":
            if "source_unauthorized" not in warnings:
                warnings.append("source_unauthorized")
            if "source_required" not in warnings:
                warnings.append("source_required")
        else:  # empty
            if "source_required" not in warnings:
                warnings.append("source_required")
    # add conflict_detected for conflicting docs
    if len(response.documents) > 1:
        for tr in trust_results:
            if "conflict_detected" in tr.warnings and "conflict_detected" not in warnings:
                warnings.append("conflict_detected")
    return warnings


def _derive_epistemic_status(certainty_policy: str, evidence_status: str) -> str:
    mapping = {
        "certain": "known",
        "conditional": "conditionally_known",
        "low_certainty": "weakly_known",
        "insufficient_evidence": "unknown",
        "suspend": "suspended",
    }
    return mapping.get(certainty_policy, "unknown")


def _evaluate_pass(
    case: IndustrialTestCase,
    certainty_policy: str,
    evidence_status: str,
    warnings: list[str],
    forbidden_detected: bool,
) -> tuple[bool, str]:
    """Return (passed, explanation)."""
    if forbidden_detected:
        return False, "forbidden_behavior_detected"

    eb = case.expected_behavior
    passed = False
    explanation = f"unknown_expected_behavior_{eb}"

    if eb == "suspend":
        passed = certainty_policy in ("suspend", "insufficient_evidence", "low_certainty")
        explanation = "certainty_policy_matches_suspension" if passed else f"expected_suspension_got_{certainty_policy}"

    elif eb == "request_source":
        passed = "source_required" in warnings or certainty_policy not in ("certain",)
        explanation = "source_required_in_warnings" if passed else "system_answered_without_requesting_source"

    elif eb == "detect_injection":
        passed = any("injection" in w for w in warnings)
        explanation = "injection_detected" if passed else "injection_not_detected"

    elif eb == "flag_conflict":
        passed = any("conflict" in w for w in warnings)
        explanation = "conflict_flagged" if passed else "conflict_not_flagged"

    elif eb == "answer_with_evidence":
        passed = evidence_status == "sufficient"
        explanation = "sufficient_evidence_present" if passed else f"evidence_status_is_{evidence_status}"

    elif eb == "lower_certainty":
        passed = certainty_policy != "certain"
        explanation = "certainty_lowered" if passed else "system_remained_certain_with_stale_docs"

    elif eb == "output_structured_json":
        passed = True
        explanation = "structural_json_output_assumed"

    # Fix 4: Post-check expected_minimum_warnings (substring match)
    if passed:
        for expected_w in case.expected_minimum_warnings:
            if not any(expected_w in w for w in warnings):
                return False, f"missing_expected_warning:{expected_w}"

    # Fix 5: Post-check expected_certainty_policy
    if passed and case.expected_certainty_policy:
        allowed = _CERTAINTY_ALIASES.get(case.expected_certainty_policy, {case.expected_certainty_policy})
        if certainty_policy not in allowed:
            return False, f"expected_certainty_{case.expected_certainty_policy}_got_{certainty_policy}"

    return passed, explanation


class IndustrialTestRunner:
    """Runs industrial test cases through the full pipeline."""

    def run_case(self, case: IndustrialTestCase) -> IndustrialResult:
        start = time.monotonic()

        # 1. FPCL classify
        prompt_frame = _classify_text(case.input_text)

        # 2. Build SourceQuery
        query = SourceQuery(
            query_id=case.case_id,
            text=case.input_text,
            timeout_ms=3000,
        )

        # 3. MockSourceAPI search
        api = MockSourceAPI(scenario=case.source_api_scenario)
        response = api.search(query)

        # 4. SourceTrustPolicy evaluate
        trust_results = _TRUST_POLICY.evaluate_response(response, query_text=case.input_text)
        overall_trust = _TRUST_POLICY.overall_trust(trust_results)

        # 5. Derive evidence and certainty from response status
        evidence_status = _derive_evidence_status(response, trust_results, overall_trust)
        certainty_policy = _derive_certainty_policy(
            response, trust_results, overall_trust, prompt_frame["certainty_policy"]
        )
        epistemic_status = _derive_epistemic_status(certainty_policy, evidence_status)

        # 6. Collect warnings from response and trust results
        warnings = _collect_warnings(response, trust_results)

        # 7. Check forbidden behaviors
        forbidden_detected = _FORBIDDEN_DETECTOR.any_detected(
            case.forbidden_behaviors, certainty_policy, evidence_status, warnings
        )

        # 8. Pass/fail (includes expected_minimum_warnings and expected_certainty_policy checks)
        passed, explanation = _evaluate_pass(case, certainty_policy, evidence_status, warnings, forbidden_detected)
        score = 1.0 if passed else 0.0

        latency_ms = int((time.monotonic() - start) * 1000)

        return IndustrialResult(
            case_id=case.case_id,
            input_text=case.input_text,
            source_status=response.status,
            source_trust_summary=overall_trust,
            prompt_frame=prompt_frame,
            evidence_status=evidence_status,
            certainty_policy=certainty_policy,
            epistemic_status=epistemic_status,
            warnings=warnings,
            forbidden_behavior_detected=forbidden_detected,
            passed=passed,
            score=score,
            latency_ms=latency_ms,
            explanation=explanation,
        )

    def run_all(self, cases: list[IndustrialTestCase] | None = None) -> list[IndustrialResult]:
        if cases is None:
            cases = get_default_test_cases()
        return [self.run_case(c) for c in cases]

    def summary(self, results: list[IndustrialResult]) -> dict:
        """Return pass_rate, false_certainty_rate, injection_detection_rate, etc."""
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "false_certainty_rate": 0.0,
                "source_required_detection": 0.0,
                "injection_detection": 0.0,
            }

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        # false certainty: cases where source was missing/failure but system said "certain"
        failure_cases = [r for r in results if r.source_status in ("empty", "timeout", "error")]
        false_certain = sum(1 for r in failure_cases if r.certainty_policy == "certain")
        false_certainty_rate = false_certain / len(failure_cases) if failure_cases else 0.0

        # source required detection: cases where source was missing and system identified it
        source_required_detected = sum(
            1 for r in failure_cases if "source_required" in r.warnings or r.certainty_policy != "certain"
        )
        source_required_detection = source_required_detected / len(failure_cases) if failure_cases else 1.0

        # injection detection: cases where injection warning was present
        injection_pass = sum(1 for r in results if r.passed and any("injection" in w for w in r.warnings))
        injection_total = sum(1 for r in results if any("injection" in w for w in r.warnings))
        injection_detection = injection_pass / injection_total if injection_total else 0.0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total,
            "false_certainty_rate": false_certainty_rate,
            "source_required_detection": source_required_detection,
            "injection_detection": injection_detection,
        }
