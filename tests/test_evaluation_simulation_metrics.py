"""Tests for simulation metrics."""
import pytest

from mcd.evaluation.simulation_metrics import (
    exact_label_match,
    partial_score_match,
    required_warning_present,
    forbidden_label_absent,
    certainty_policy_match,
    evidence_need_match,
    schema_completeness,
    structured_reasoning_score,
    score_example,
    EvaluationScore,
)


def test_exact_label_match_correct():
    assert exact_label_match("epistemic", "epistemic") == 1.0


def test_exact_label_match_wrong():
    assert exact_label_match("shari", "epistemic") == 0.0


def test_exact_label_match_list():
    assert exact_label_match("epistemic", ["epistemic", "value"]) == 1.0


def test_partial_score_match():
    assert partial_score_match(["epistemic", "value"], ["epistemic", "value", "shari"]) == pytest.approx(2/3, abs=0.01)


def test_required_warning_present_found():
    assert required_warning_present(["shari judgment requires shari evidence"], "shari") == 1.0


def test_required_warning_present_missing():
    assert required_warning_present(["some other warning"], "shari") == 0.0


def test_forbidden_label_absent_ok():
    assert forbidden_label_absent(["epistemic"], "shari") == 1.0


def test_forbidden_label_absent_violation():
    assert forbidden_label_absent(["epistemic", "shari"], "shari") == 0.0


def test_certainty_policy_match_hit():
    assert certainty_policy_match("suspend", ["suspend", "hypothesis"]) == 1.0


def test_certainty_policy_match_miss():
    assert certainty_policy_match("near_certainty", ["suspend"]) == 0.0


def test_schema_completeness_full():
    output = {"judgment_types": {}, "evidence_needs": {}, "certainty_policy": "x", "root_domain": {}}
    assert schema_completeness(output, ["judgment_types", "evidence_needs", "certainty_policy", "root_domain"]) == 1.0


def test_schema_completeness_partial():
    output = {"judgment_types": {}}
    assert schema_completeness(output, ["judgment_types", "evidence_needs"]) == 0.5


def test_structured_reasoning_score_full():
    output = {"judgment_types": {}, "evidence_needs": {}, "certainty_policy": "x", "root_domain": {}}
    assert structured_reasoning_score(output) == 1.0


def test_score_example_returns_score():
    frame_dict = {
        "judgment_types": {"epistemic": 0.8},
        "evidence_needs": {"sensory": 0.7},
        "certainty_policy": "near_certainty",
        "root_domain": {"universe": 0.9},
        "warnings": [],
    }
    expected = {
        "judgment_type": "epistemic",
        "certainty_policy": ["strong_knowledge", "near_certainty"],
        "should_suspend": False,
    }
    score = score_example("BM-01", expected, frame_dict)
    assert isinstance(score, EvaluationScore)
    assert 0.0 <= score.total_score <= 1.0
