"""Tests for CertaintyCalibration — Phase 2 calibration module."""
import pytest

from mcd.evaluation.certainty_calibration import (
    CertaintyCalibration,
    CalibrationReport,
    DimensionCalibration,
    _is_suspended,
    _high_certainty,
    _predicted_judgment_types,
    _score_judgment_type,
    _score_certainty_policy,
    _score_suspension,
    _score_false_certainty,
    _score_harm_haram,
    _score_ambiguity_handling,
)
from mcd.evaluation.benchmark_dataset import BenchmarkExample


# ─── Helper factories ─────────────────────────────────────────────────────────

def _frame(
    judgment_types: dict | None = None,
    certainty_policy: str = "strong_knowledge",
    warnings: list | None = None,
) -> dict:
    return {
        "judgment_types": judgment_types or {},
        "evidence_needs": {},
        "certainty_policy": certainty_policy,
        "root_domain": {},
        "warnings": warnings or [],
    }


def _example(
    example_id: str = "TEST-01",
    input_text: str = "النار تحرق",
    expected_behavior: dict | None = None,
) -> BenchmarkExample:
    return BenchmarkExample(
        example_id=example_id,
        input_text=input_text,
        task_type="test",
        expected_behavior=expected_behavior or {},
    )


# ─── Unit tests for helpers ───────────────────────────────────────────────────

def test_is_suspended_true():
    assert _is_suspended({"certainty_policy": "suspend"}) is True


def test_is_suspended_false():
    assert _is_suspended({"certainty_policy": "strong_knowledge"}) is False


def test_high_certainty_near_certainty():
    assert _high_certainty({"certainty_policy": "near_certainty"}) is True


def test_high_certainty_strong_knowledge():
    assert _high_certainty({"certainty_policy": "strong_knowledge"}) is True


def test_high_certainty_false_for_hypothesis():
    assert _high_certainty({"certainty_policy": "hypothesis"}) is False


def test_predicted_judgment_types():
    fd = _frame(judgment_types={"epistemic": 0.4, "value": 0.3})
    result = _predicted_judgment_types(fd)
    assert "epistemic" in result
    assert "value" in result


# ─── Unit tests for dimension scorers ────────────────────────────────────────

def test_score_judgment_type_correct_single():
    ex = _example(expected_behavior={"judgment_type": "epistemic"})
    fd = _frame(judgment_types={"epistemic": 0.4})
    ok, msg = _score_judgment_type(ex, fd)
    assert ok is True
    assert msg == ""


def test_score_judgment_type_correct_list():
    ex = _example(expected_behavior={"judgment_type": ["epistemic", "value"]})
    fd = _frame(judgment_types={"epistemic": 0.4})
    ok, msg = _score_judgment_type(ex, fd)
    assert ok is True


def test_score_judgment_type_fail():
    ex = _example(expected_behavior={"judgment_type": "shari"})
    fd = _frame(judgment_types={"epistemic": 0.4})
    ok, msg = _score_judgment_type(ex, fd)
    assert ok is False
    assert "shari" in msg


def test_score_certainty_policy_correct():
    ex = _example(expected_behavior={"certainty_policy": ["strong_knowledge", "near_certainty"]})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_certainty_policy(ex, fd)
    assert ok is True


def test_score_certainty_policy_fail():
    ex = _example(expected_behavior={"certainty_policy": ["suspend"]})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_certainty_policy(ex, fd)
    assert ok is False
    assert "strong_knowledge" in msg


def test_score_suspension_should_suspend_and_does():
    ex = _example(expected_behavior={"should_suspend": True})
    fd = _frame(certainty_policy="suspend")
    ok, msg = _score_suspension(ex, fd)
    assert ok is True


def test_score_suspension_should_not_suspend_and_does_not():
    ex = _example(expected_behavior={"should_suspend": False})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_suspension(ex, fd)
    assert ok is True


def test_score_suspension_fail():
    ex = _example(expected_behavior={"should_suspend": True})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_suspension(ex, fd)
    assert ok is False
    assert "expected=True" in msg


def test_score_false_certainty_no_false_certainty():
    ex = _example(expected_behavior={"should_suspend": True})
    fd = _frame(certainty_policy="suspend")
    ok, msg = _score_false_certainty(ex, fd)
    assert ok is True


def test_score_false_certainty_detected():
    ex = _example(expected_behavior={"should_suspend": True})
    fd = _frame(certainty_policy="near_certainty")
    ok, msg = _score_false_certainty(ex, fd)
    assert ok is False
    assert "false certainty" in msg


def test_score_harm_haram_correct():
    ex = _example(expected_behavior={"harm_haram_separation": True})
    fd = _frame(judgment_types={"shari": 0.9}, warnings=["shari judgment requires shari evidence"])
    ok, msg = _score_harm_haram(ex, fd, fd["warnings"])
    assert ok is True


def test_score_harm_haram_fail():
    ex = _example(expected_behavior={"harm_haram_separation": True})
    fd = _frame(judgment_types={"value": 0.9}, warnings=[])
    ok, msg = _score_harm_haram(ex, fd, fd["warnings"])
    assert ok is False


def test_score_ambiguity_handling_correct():
    ex = _example(expected_behavior={"judgment_type": "ambiguous"})
    fd = _frame(certainty_policy="suspend")
    ok, msg = _score_ambiguity_handling(ex, fd)
    assert ok is True


def test_score_ambiguity_handling_fail():
    ex = _example(expected_behavior={"judgment_type": "ambiguous"})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_ambiguity_handling(ex, fd)
    assert ok is False


def test_score_ambiguity_handling_skip_non_ambiguous():
    ex = _example(expected_behavior={"judgment_type": "technical"})
    fd = _frame(certainty_policy="strong_knowledge")
    ok, msg = _score_ambiguity_handling(ex, fd)
    assert ok is True  # Not an ambiguity case — skip


# ─── DimensionCalibration ────────────────────────────────────────────────────

def test_dimension_calibration_to_dict():
    dim = DimensionCalibration(
        dimension="judgment_type_accuracy",
        correct=7,
        total=10,
        accuracy=0.70,
        failures=["ex-1: failed"],
    )
    d = dim.to_dict()
    assert d["dimension"] == "judgment_type_accuracy"
    assert d["correct"] == 7
    assert d["total"] == 10
    assert d["accuracy"] == 0.70
    assert len(d["failures"]) == 1


# ─── Integration tests ────────────────────────────────────────────────────────

def test_calibration_run_returns_report():
    cal = CertaintyCalibration()
    report = cal.run()
    assert isinstance(report, CalibrationReport)
    assert report.total_examples == 50


def test_calibration_report_has_six_dimensions():
    cal = CertaintyCalibration()
    report = cal.run()
    dim_names = {d.dimension for d in report.dimensions}
    assert "judgment_type_accuracy" in dim_names
    assert "certainty_policy_accuracy" in dim_names
    assert "suspension_correctness" in dim_names
    assert "false_certainty_absence" in dim_names
    assert "harm_haram_separation" in dim_names
    assert "ambiguity_handling" in dim_names


def test_calibration_overall_accuracy_in_range():
    cal = CertaintyCalibration()
    report = cal.run()
    assert 0.0 <= report.overall_accuracy <= 1.0


def test_calibration_score_in_range():
    cal = CertaintyCalibration()
    report = cal.run()
    assert 0.0 <= report.calibration_score <= 1.0


def test_calibration_false_certainty_rate_in_range():
    cal = CertaintyCalibration()
    report = cal.run()
    assert 0.0 <= report.false_certainty_rate <= 1.0


def test_calibration_suspension_precision_recall_in_range():
    cal = CertaintyCalibration()
    report = cal.run()
    assert 0.0 <= report.suspension_precision <= 1.0
    assert 0.0 <= report.suspension_recall <= 1.0


def test_calibration_has_recommendations():
    cal = CertaintyCalibration()
    report = cal.run()
    assert isinstance(report.recommendations, list)
    assert len(report.recommendations) >= 1


def test_calibration_to_dict_structure():
    cal = CertaintyCalibration()
    report = cal.run()
    d = report.to_dict()
    assert "total_examples" in d
    assert "overall_accuracy" in d
    assert "calibration_score" in d
    assert "false_certainty_rate" in d
    assert "suspension_precision" in d
    assert "suspension_recall" in d
    assert "dimensions" in d
    assert "recommendations" in d


def test_calibration_dimension_totals_nonzero():
    cal = CertaintyCalibration()
    report = cal.run()
    for dim in report.dimensions:
        assert dim.total >= 0


def test_calibration_custom_examples():
    """Calibration can run on a custom example list."""
    examples = [
        BenchmarkExample(
            example_id="CUSTOM-01",
            input_text="النار تحرق",
            task_type="epistemic",
            expected_behavior={
                "judgment_type": "epistemic",
                "certainty_policy": ["strong_knowledge", "near_certainty"],
                "should_suspend": False,
            },
        )
    ]
    cal = CertaintyCalibration()
    report = cal.run(examples=examples)
    assert report.total_examples == 1
    assert 0.0 <= report.overall_accuracy <= 1.0


def test_calibration_harm_haram_dimension_has_examples():
    """The harm-haram dimension should have at least one test case in the full dataset."""
    cal = CertaintyCalibration()
    report = cal.run()
    hh = next((d for d in report.dimensions if d.dimension == "harm_haram_separation"), None)
    assert hh is not None
    assert hh.total >= 1
