from __future__ import annotations

from mcd.evaluation.fractal_baseline_comparison import (
    ConservativeHypothesisBaseline,
    GovernedProtocolBaseline,
    run_fractal_baseline_comparison,
)
from mcd.evaluation.fractal_benchmark_dataset import (
    benchmark_dataset_summary,
    iter_all_cases,
    validate_all_cases,
)


REQUIRED_METRICS = {
    "false_certificate_rate",
    "overblocking_rate",
    "residual_preservation_rate",
    "reverse_trace_coverage",
    "forbidden_transition_violation_rate",
    "zero_in_path_locality_accuracy",
    "decision_calibration_error",
    "gettier_detection_rate",
}


def _baseline(report: dict[str, object], name: str) -> dict[str, object]:
    return report["baselines"][name]


def test_report_has_required_top_level_contracts():
    report = run_fractal_baseline_comparison()
    assert report["protocol_id"] == "FRACTAL-BASELINE-COMPARISON-106"
    assert report["dataset_id"] == "fractal_governance_benchmark_105"
    assert report["deterministic"] is True
    assert report["trained_model_used"] is False
    assert report["external_models_used"] == []
    assert report["theorem_status"] == "STRONG_HYPOTHESIS"
    assert report["final_epistemic_judgments"] == ["ZERO", "HYPOTHESIS", "CERTIFICATE"]
    assert set(report["baselines"].keys()) == {
        "AnswerConfidenceBaseline",
        "NaiveCertificateBaseline",
        "ConservativeHypothesisBaseline",
        "GovernedProtocolBaseline",
    }


def test_all_baselines_expose_the_eight_metrics():
    report = run_fractal_baseline_comparison()
    for baseline_data in report["baselines"].values():
        metrics = baseline_data["metrics"]
        assert REQUIRED_METRICS.issubset(metrics.keys())


def test_answer_confidence_baseline_can_issue_false_certificates():
    report = run_fractal_baseline_comparison()
    metric = _baseline(report, "AnswerConfidenceBaseline")["metrics"]["false_certificate_rate"]
    assert metric > 0.0


def test_governed_protocol_reduces_false_certificate_rate():
    report = run_fractal_baseline_comparison()
    governed = _baseline(report, "GovernedProtocolBaseline")["metrics"]["false_certificate_rate"]
    naive = _baseline(report, "NaiveCertificateBaseline")["metrics"]["false_certificate_rate"]
    assert governed <= naive


def test_governed_protocol_preserves_residuals():
    report = run_fractal_baseline_comparison()
    metric = _baseline(report, "GovernedProtocolBaseline")["metrics"]["residual_preservation_rate"]
    assert metric == 1.0


def test_governed_protocol_preserves_zero_in_path_locality():
    report = run_fractal_baseline_comparison()
    metric = _baseline(report, "GovernedProtocolBaseline")["metrics"]["zero_in_path_locality_accuracy"]
    assert metric == 1.0


def test_governed_protocol_requires_reverse_trace_for_strong_or_candidate():
    case = next(row for row in iter_all_cases() if row["id"] == "math-triangle-euclidean-002").copy()
    case["reverse_trace_required"] = False
    case["trace_definition"] = {}
    result = GovernedProtocolBaseline().predict(case)
    assert result.predicted_decision == "HYPOTHESIS"


def test_gettier_style_cases_cannot_become_certificate_under_governed_protocol():
    report = run_fractal_baseline_comparison()
    governed_cases = _baseline(report, "GovernedProtocolBaseline")["cases"]
    gettier_cases = [
        row
        for row in governed_cases
        if "gettier" in row["case_id"].lower() or "gettier_failure" in row["error_tags"]
    ]
    assert gettier_cases
    assert all(row["predicted_decision"] != "CERTIFICATE" for row in gettier_cases)


def test_conservative_overblocks_more_than_governed():
    report = run_fractal_baseline_comparison()
    conservative = _baseline(report, "ConservativeHypothesisBaseline")["metrics"]["overblocking_rate"]
    governed = _baseline(report, "GovernedProtocolBaseline")["metrics"]["overblocking_rate"]
    assert conservative > governed


def test_no_model_training_performed_and_theorem_status_unchanged():
    report = run_fractal_baseline_comparison()
    summary = benchmark_dataset_summary()
    assert report["trained_model_used"] is False
    assert summary["theorem_status"] == "STRONG_HYPOTHESIS"
    assert report["theorem_status"] == "STRONG_HYPOTHESIS"


def test_dataset_contract_remains_valid_and_case_count_unchanged():
    assert validate_all_cases() == {}
    report = run_fractal_baseline_comparison()
    case_count = len(iter_all_cases())
    governed_case_count = len(_baseline(report, "GovernedProtocolBaseline")["cases"])
    assert governed_case_count == case_count


def test_results_are_deterministic():
    first = run_fractal_baseline_comparison()
    second = run_fractal_baseline_comparison()
    assert first == second


def test_governed_baseline_only_certifies_with_full_obligations_when_it_certifies():
    report = run_fractal_baseline_comparison()
    governed_cases = _baseline(report, "GovernedProtocolBaseline")["cases"]
    certificates = [row for row in governed_cases if row["predicted_decision"] == "CERTIFICATE"]
    assert all(
        row["evidence_complete"]
        and row["governance_gate_passed"]
        and row["reverse_trace_complete"]
        and not row["has_blocking_residual"]
        for row in certificates
    )


def test_conservative_baseline_exists_as_required_model():
    baseline = ConservativeHypothesisBaseline()
    case = next(row for row in iter_all_cases())
    result = baseline.predict(case)
    assert result.baseline == "ConservativeHypothesisBaseline"
