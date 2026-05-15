from __future__ import annotations

from mcd.evaluation.fractal_benchmark_dataset import (
    DOMAIN_FILES,
    iter_all_cases,
    load_all_domain_cases,
    validate_all_cases,
    validate_case,
)
from mcd.evaluation.fractal_embedding_measurement_protocol import (
    BenchmarkCase,
    DecisionGate,
    LOCAL_ZERO_IN_PATH,
    aggregate_global_status,
    compute_measurement_metrics,
    decide_status,
)


def _to_benchmark_case(row: dict[str, object]) -> BenchmarkCase:
    return BenchmarkCase(
        case_id=str(row["id"]),
        domain=str(row["domain"]),
        input_text=str(row["input"]),
        candidates=tuple(str(item) for item in row["candidates"]),
        constraints=tuple(str(item) for item in row["constraints"]),
        required_evidence=tuple(str(item) for item in row["required_evidence"]),
        expected_residuals=tuple(str(item) for item in row["expected_residuals"]),
        forbidden_decisions=tuple(str(item) for item in row["forbidden_decisions"]),
        allowed_decision_level=str(row["allowed_decision_level"]),
        reverse_trace_requirement=(
            "reverse_trace_required"
            if bool(row["reverse_trace_required"])
            else "reverse_trace_optional"
        ),
    )


def test_all_benchmark_files_load():
    loaded = load_all_domain_cases()
    assert set(loaded.keys()) == set(DOMAIN_FILES.keys())
    assert all(isinstance(rows, list) and rows for rows in loaded.values())


def test_each_domain_has_at_least_three_cases():
    loaded = load_all_domain_cases()
    assert all(len(rows) >= 3 for rows in loaded.values())


def test_every_case_validates_against_contract_and_benchmark_case_mapping():
    assert validate_all_cases() == {}
    for row in iter_all_cases():
        mapped = _to_benchmark_case(row)
        assert mapped.case_id
        assert mapped.domain == row["domain"]


def test_cases_distinguish_answer_likelihood_from_justified_decision():
    has_candidate = False
    for row in iter_all_cases():
        level = row["allowed_decision_level"]
        forbidden = set(row["forbidden_decisions"])
        if level in {"ZERO", "HYPOTHESIS", "STRONG"}:
            assert "CERTIFICATE" in forbidden
        if level in {"CERTIFICATE_CANDIDATE", "CERTIFICATE"}:
            has_candidate = True
            assert bool(row["reverse_trace_required"]) is True
    assert has_candidate


def test_smoke_fire_case_forbids_certificate():
    case = next(row for row in iter_all_cases() if row["id"] == "physical-smoke-001")
    assert "CERTIFICATE" in case["forbidden_decisions"]
    assert case["allowed_decision_level"] == "HYPOTHESIS"


def test_ci_pass_only_case_forbids_certificate():
    case = next(row for row in iter_all_cases() if row["id"] == "coding-ci-pass-001")
    assert "CERTIFICATE" in case["forbidden_decisions"]
    assert case["allowed_decision_level"] == "HYPOTHESIS"


def test_ambiguous_arabic_token_remains_hypothesis():
    case = next(row for row in iter_all_cases() if row["id"] == "arabic-ala-no-context-001")
    assert case["allowed_decision_level"] == "HYPOTHESIS"
    assert "CERTIFICATE" in case["forbidden_decisions"]


def test_arabic_metaphor_case_is_strong_with_residual_certificate_block_only():
    case = next(row for row in iter_all_cases() if row["id"] == "arabic-ala-metaphor-003")
    assert case["expected_decision_level"] == "STRONG"
    assert case["allowed_decision_level"] == "STRONG"
    assert "CERTIFICATE" in case["forbidden_decisions"]
    assert case["expected_residuals"]
    assert bool(case["reverse_trace_required"]) is True
    assert isinstance(case["trace_definition"], dict) and case["trace_definition"]


def test_missing_assumptions_triangle_stays_hypothesis_and_forbids_strong_and_candidate():
    case = next(
        row for row in iter_all_cases() if row["id"] == "math-triangle-missing-assumptions-003"
    )
    assert case["expected_decision_level"] == "HYPOTHESIS"
    assert case["allowed_decision_level"] == "HYPOTHESIS"
    assert {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}.issubset(
        set(case["forbidden_decisions"])
    )
    assert {
        "missing_geometry_assumption",
        "missing_formal_proof_obligation",
    }.issubset(set(case["expected_residuals"]))
    assert case["trace_definition"].get("trace_status") == "incomplete_for_certificate"


def test_euclidean_triangle_is_candidate_but_not_global_certificate_without_gate():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002")
    assert case["allowed_decision_level"] == "CERTIFICATE_CANDIDATE"
    assert case["expected_decision_level"] == "CERTIFICATE_CANDIDATE"

    blocked_gate = DecisionGate(
        evidence_present=True,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="",
        blocking_residual_present=False,
    )
    local_status = decide_status(0.99, blocked_gate)
    assert local_status != "CERTIFICATE"
    assert aggregate_global_status([local_status, "HYPOTHESIS"]) == "HYPOTHESIS"


def test_zero_in_path_local_cases_exist_in_each_domain():
    all_cases = iter_all_cases()
    by_domain = {domain: [] for domain in DOMAIN_FILES}
    for row in all_cases:
        if bool(row.get("local_zero_in_path")):
            by_domain[row["domain"]].append(row)

    assert all(by_domain[domain] for domain in DOMAIN_FILES)


def test_zero_in_path_local_cases_preserve_remaining_paths_and_not_global_zero():
    for row in iter_all_cases():
        if not bool(row.get("local_zero_in_path")):
            continue
        assert row.get("global_zero") is False
        assert isinstance(row.get("blocked_path"), str) and row["blocked_path"]
        assert isinstance(row.get("remaining_paths"), list) and row["remaining_paths"]
        assert aggregate_global_status([LOCAL_ZERO_IN_PATH, "HYPOTHESIS"]) == "HYPOTHESIS"


def test_validator_rejects_strong_without_reverse_trace():
    case = next(row for row in iter_all_cases() if row["id"] == "arabic-ala-context-002").copy()
    case["reverse_trace_required"] = False
    errors = validate_case(case)
    assert any("STRONG/CERTIFICATE_CANDIDATE cases require reverse_trace_required=true" in e for e in errors)


def test_validator_rejects_strong_without_trace_definition():
    case = next(row for row in iter_all_cases() if row["id"] == "arabic-ala-context-002").copy()
    case["trace_definition"] = {}
    errors = validate_case(case)
    assert any("trace_definition" in e for e in errors)


def test_validator_rejects_candidate_without_trace_definition():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002").copy()
    case["trace_definition"] = {}
    errors = validate_case(case)
    assert any("trace_definition" in e for e in errors)


def test_validator_rejects_candidate_without_required_evidence():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002").copy()
    case["required_evidence"] = []
    errors = validate_case(case)
    assert any("CERTIFICATE_CANDIDATE requires non-empty required_evidence" in e for e in errors)


def test_validator_rejects_certificate_without_full_obligations():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002").copy()
    case["allowed_decision_level"] = "CERTIFICATE"
    case["expected_decision_level"] = "CERTIFICATE"
    case["certificate_obligations"] = {
        "proof_object": True,
        "governance_gate_passed": True,
        "reverse_trace_complete": False,
        "evidence_complete": True,
        "no_blocking_residual": True,
    }
    errors = validate_case(case)
    assert any("CERTIFICATE level requires explicit certificate obligations" in e for e in errors)


def test_high_answer_likelihood_missing_evidence_remains_hypothesis():
    blocked_gate = DecisionGate(
        evidence_present=False,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
        blocking_residual_present=False,
    )
    assert decide_status(0.99, blocked_gate) == "HYPOTHESIS"


def test_complete_answer_missing_trace_cannot_be_certificate():
    blocked_gate = DecisionGate(
        evidence_present=True,
        reverse_trace_complete=False,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
        blocking_residual_present=False,
    )
    assert decide_status(0.99, blocked_gate) != "CERTIFICATE"


def test_blocking_residual_cannot_be_certificate():
    blocked_gate = DecisionGate(
        evidence_present=True,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
        blocking_residual_present=True,
    )
    assert decide_status(0.99, blocked_gate) != "CERTIFICATE"


def test_false_certificate_rate_metric_readiness():
    metrics = compute_measurement_metrics(
        [
            {
                "issued_certificate": True,
                "certificate_justified": False,
                "decision_confidence": 0.99,
                "decision_correct": True,
            },
            {
                "issued_certificate": False,
                "certificate_justified": False,
                "decision_confidence": 0.8,
                "decision_correct": True,
            },
        ]
    )
    assert "false_certificate_rate" in metrics
    assert metrics["false_certificate_rate"] == 1.0


def test_all_cases_forbidding_certificate_are_discoverable():
    forbidders = [row for row in iter_all_cases() if "CERTIFICATE" in row["forbidden_decisions"]]
    assert forbidders
    ids = {row["id"] for row in forbidders}
    assert "coding-ci-pass-001" in ids
    assert "physical-smoke-001" in ids
    assert "arabic-ala-no-context-001" in ids


def test_gettier_style_case_exists_and_blocks_certificate():
    gettier_cases = [
        row
        for row in iter_all_cases()
        if "gettier" in str(row["id"]).lower() or "Gettier-style" in str(row["notes"])
    ]
    assert gettier_cases
    for row in gettier_cases:
        assert row["allowed_decision_level"] in {"HYPOTHESIS", "ZERO"}
        assert "CERTIFICATE" in row["forbidden_decisions"]
