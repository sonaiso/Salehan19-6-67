from __future__ import annotations

from mcd.evaluation.fractal_benchmark_dataset import (
    DOMAIN_FILES,
    iter_all_cases,
    load_all_domain_cases,
    validate_all_cases,
)
from mcd.evaluation.fractal_embedding_measurement_protocol import (
    BenchmarkCase,
    DecisionGate,
    LOCAL_ZERO_IN_PATH,
    aggregate_global_status,
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


def test_euclidean_triangle_is_candidate_but_not_global_certificate_without_gate():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002")
    assert case["allowed_decision_level"] == "CERTIFICATE_CANDIDATE"

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


def test_zero_in_path_remains_local():
    local_case = next(
        row for row in iter_all_cases() if row["id"] == "coding-zero-in-path-local-003"
    )
    assert local_case["allowed_decision_level"] == "HYPOTHESIS"
    assert aggregate_global_status([LOCAL_ZERO_IN_PATH, "HYPOTHESIS"]) == "HYPOTHESIS"
