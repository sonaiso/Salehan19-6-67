from __future__ import annotations

from mcd.evaluation.prior_aware_baseline_ablation import (
    MODE_WITH_GOLDEN_PRIORS,
    MODE_WITHOUT_PRIORS,
    run_prior_aware_baseline_ablation,
)
from mcd.knowledge.golden_prior_registry import PriorRegistry


def _mode(report: dict[str, object], name: str) -> dict[str, object]:
    return report["modes"][name]


def _case(report: dict[str, object], mode_name: str, case_id: str) -> dict[str, object]:
    rows = _mode(report, mode_name)["cases"]
    return next(row for row in rows if row["case_id"] == case_id)


def _matrix_case(report: dict[str, object], mode_name: str, case_id: str) -> dict[str, object]:
    rows = _mode(report, mode_name)["prior_coverage_matrix"]
    return next(row for row in rows if row["case_id"] == case_id)


def test_runner_compares_without_prior_and_with_prior_modes():
    report = run_prior_aware_baseline_ablation()
    assert MODE_WITHOUT_PRIORS in report["modes"]
    assert MODE_WITH_GOLDEN_PRIORS in report["modes"]


def test_prior_aware_mode_reduces_or_blocks_false_certificates_in_known_cases():
    report = run_prior_aware_baseline_ablation()
    no_prior = _mode(report, MODE_WITHOUT_PRIORS)["metrics"]["false_certificate_rate"]
    with_prior = _mode(report, MODE_WITH_GOLDEN_PRIORS)["metrics"]["false_certificate_rate"]
    assert with_prior <= no_prior


def test_prior_aware_mode_does_not_downgrade_arabic_ala_metaphor_003_below_strong():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "arabic-ala-metaphor-003")
    assert case["predicted_decision"] in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}


def test_prior_aware_mode_blocks_smoke_only_to_fire_certificate():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "physical-smoke-001")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "physical-smoke-001")
    assert case["predicted_decision"] != "CERTIFICATE"
    assert "smoke_only_not_certificate" in matrix["certificate_blockers_activated"]


def test_prior_aware_mode_blocks_ci_pass_to_certificate():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "coding-ci-pass-001")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "coding-ci-pass-001")
    assert case["predicted_decision"] != "CERTIFICATE"
    assert "ci_pass_to_certificate" in matrix["certificate_blockers_activated"]


def test_prior_aware_mode_blocks_triangle_without_geometry_scope_to_certificate():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "math-triangle-001")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "math-triangle-001")
    assert case["predicted_decision"] != "CERTIFICATE"
    assert "triangle_missing_geometry_scope" in matrix["certificate_blockers_activated"]


def test_missing_prior_rule_emits_prior_coverage_gap_residual():
    report = run_prior_aware_baseline_ablation(prior_registry=PriorRegistry())
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "coding-governed-pr-002")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "coding-governed-pr-002")
    assert matrix["missing_prior_rule"] is True
    assert "prior_coverage_gap" in matrix["prior_residuals"]
    assert case["predicted_decision"] != "CERTIFICATE"


def test_prior_metrics_and_overblocking_delta_are_computed():
    report = run_prior_aware_baseline_ablation()
    metrics = _mode(report, MODE_WITH_GOLDEN_PRIORS)["metrics"]
    assert "prior_rule_coverage_rate" in metrics
    assert "prior_blocker_activation_rate" in metrics
    assert "prior_missing_evidence_rate" in metrics
    assert "prior_coverage_gap_count" in metrics
    assert "prior_overblocking_delta" in report["deltas"]


def test_theorem_status_and_non_goals_remain_enforced():
    report = run_prior_aware_baseline_ablation()
    assert report["theorem_status"] == "STRONG_HYPOTHESIS"
    assert report["trained_model_used"] is False
    assert report["external_models_used"] == []
    assert report["artificial_consciousness_claim"] is False


def test_reports_are_deterministic():
    first = run_prior_aware_baseline_ablation()
    second = run_prior_aware_baseline_ablation()
    assert first == second
