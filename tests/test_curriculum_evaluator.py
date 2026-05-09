"""Tests for CurriculumEvaluator."""
from __future__ import annotations

import pytest
from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator, CurriculumEvaluationReport
from mcd.curriculum.curriculum_generator import CurriculumGenerator
from mcd.curriculum.curriculum_dataset import CurriculumDataset


def test_evaluate_returns_report():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10)
    report = CurriculumEvaluator().evaluate(units)
    assert isinstance(report, CurriculumEvaluationReport)


def test_evaluate_total_units():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10)
    report = CurriculumEvaluator().evaluate(units)
    assert report.total_units == 10


def test_evaluate_overall_score_positive():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    report = CurriculumEvaluator().evaluate(units)
    assert report.overall_score > 0.0


def test_evaluate_score_by_level_populated():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    report = CurriculumEvaluator().evaluate(units)
    assert len(report.score_by_level) == 8


def test_evaluate_score_by_layer_populated():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    report = CurriculumEvaluator().evaluate(units)
    assert len(report.score_by_layer) > 0


def test_evaluate_empty_units():
    report = CurriculumEvaluator().evaluate([])
    assert report.total_units == 0
    assert report.overall_score == 0.0


def test_evaluate_recommendations_populated():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    report = CurriculumEvaluator().evaluate(units)
    assert len(report.recommendations) > 0


def test_evaluate_to_dict_has_expected_keys():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 5)
    report = CurriculumEvaluator().evaluate(units)
    d = report.to_dict()
    for key in ["total_units", "overall_score", "score_by_level", "score_by_layer",
                "failed_units", "recommendations", "metrics"]:
        assert key in d


def test_evaluate_metrics_in_to_dict():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    report = CurriculumEvaluator().evaluate(units)
    d = report.to_dict()
    metrics = d["metrics"]
    for key in ["thing_detection_accuracy", "property_detection_accuracy",
                "action_detection_accuracy", "relation_detection_accuracy",
                "evidence_need_accuracy", "certainty_policy_accuracy"]:
        assert key in metrics


def test_evaluate_full_dataset():
    ds = CurriculumDataset()
    units = ds.load_all()
    report = CurriculumEvaluator().evaluate(units)
    assert report.total_units >= 800
    assert report.overall_score > 0.0
