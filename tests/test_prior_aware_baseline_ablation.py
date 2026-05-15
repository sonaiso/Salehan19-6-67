from __future__ import annotations

from mcd.evaluation.prior_aware_baseline_ablation import (
    MODE_PRIOR_BLOCKERS_ONLY,
    MODE_PRIOR_EVIDENCE_ONLY,
    MODE_PRIOR_RESIDUALS_ONLY,
    MODE_WITH_GOLDEN_PRIORS,
    MODE_WITH_QUALIFIED_GOLDEN_RULES,
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


def test_runner_exposes_all_required_modes():
    report = run_prior_aware_baseline_ablation()
    assert MODE_WITHOUT_PRIORS in report["modes"]
    assert MODE_WITH_GOLDEN_PRIORS in report["modes"]
    assert MODE_WITH_QUALIFIED_GOLDEN_RULES in report["modes"]
    assert MODE_PRIOR_BLOCKERS_ONLY in report["modes"]
    assert MODE_PRIOR_EVIDENCE_ONLY in report["modes"]
    assert MODE_PRIOR_RESIDUALS_ONLY in report["modes"]


def test_golden_rule_modes_reduce_or_block_false_certificates():
    report = run_prior_aware_baseline_ablation()
    no_prior = _mode(report, MODE_WITHOUT_PRIORS)["metrics"]["false_certificate_rate"]
    with_prior = _mode(report, MODE_WITH_GOLDEN_PRIORS)["metrics"]["false_certificate_rate"]
    with_golden_only = _mode(report, MODE_WITH_QUALIFIED_GOLDEN_RULES)["metrics"]["false_certificate_rate"]
    assert with_prior <= no_prior
    assert with_golden_only <= no_prior


def test_arabic_ala_metaphor_not_downgraded_below_strong():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "arabic-ala-metaphor-003")
    assert case["predicted_decision"] in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}


def test_smoke_only_to_fire_certificate_is_blocked():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "physical-smoke-001")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "physical-smoke-001")
    assert case["predicted_decision"] != "CERTIFICATE"
    assert "smoke_only_not_certificate" in matrix["certificate_blockers_activated"]


def test_ci_pass_to_certificate_is_blocked():
    report = run_prior_aware_baseline_ablation()
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "coding-ci-pass-001")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "coding-ci-pass-001")
    assert case["predicted_decision"] != "CERTIFICATE"
    assert "ci_pass_to_certificate" in matrix["certificate_blockers_activated"]


def test_missing_golden_rule_emits_golden_rule_coverage_gap_residual():
    report = run_prior_aware_baseline_ablation(prior_registry=PriorRegistry())
    case = _case(report, MODE_WITH_GOLDEN_PRIORS, "coding-governed-pr-002")
    matrix = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "coding-governed-pr-002")
    assert matrix["missing_golden_rule"] is True
    assert "golden_rule_coverage_gap" in matrix["residuals_added_by_priors"]
    assert case["predicted_decision"] != "CERTIFICATE"


def test_required_metrics_and_deltas_exist():
    report = run_prior_aware_baseline_ablation()
    metrics = _mode(report, MODE_WITH_GOLDEN_PRIORS)["metrics"]
    assert "prior_rule_coverage_rate" in metrics
    assert "golden_rule_coverage_rate" in metrics
    assert "golden_rule_activation_rate" in metrics
    assert "certificate_blocker_activation_rate" in metrics
    assert "missing_evidence_rate" in metrics
    assert "concept_admissibility_block_rate" in metrics
    assert "uncovered_case_rate" in metrics

    assert "false_certificate_delta" in report["deltas"]
    assert "overblocking_delta" in report["deltas"]
    assert "residual_preservation_delta" in report["deltas"]


def test_matrix_contains_required_coverage_fields():
    report = run_prior_aware_baseline_ablation()
    row = _matrix_case(report, MODE_WITH_GOLDEN_PRIORS, "coding-ci-pass-001")
    required = {
        "matched_prior_rule_ids",
        "matched_golden_rule_ids",
        "missing_prior_rule",
        "missing_golden_rule",
        "prior_maturity_level",
        "certificate_blockers_activated",
        "missing_evidence_detected",
        "residuals_added_by_priors",
        "decision_before_priors",
        "decision_after_priors",
        "decision_after_golden_rules_only",
        "decision_delta",
    }
    assert required.issubset(set(row.keys()))


def test_theorem_status_and_non_goals_remain_enforced():
    report = run_prior_aware_baseline_ablation()
    assert report["theorem_status"] == "STRONG_HYPOTHESIS"
    assert report["trained_model_used"] is False
    assert report["external_models_used"] == []
    assert report["artificial_consciousness_claim"] is False
    assert report["global_certificate_claim"] is False


def test_reports_are_deterministic():
    first = run_prior_aware_baseline_ablation()
    second = run_prior_aware_baseline_ablation()
    assert first == second
