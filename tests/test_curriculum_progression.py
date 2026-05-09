"""Tests for ProgressionTracker."""
from __future__ import annotations

import pytest
from mcd.curriculum.progression import ProgressionTracker, ProgressionReport, ProgressionStep
from mcd.curriculum.curriculum_generator import CurriculumGenerator
from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator


def test_compute_returns_report():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 5)
    scores = {u.unit_id: 0.8 for u in units}
    report = ProgressionTracker().compute(units, scores)
    assert isinstance(report, ProgressionReport)


def test_compute_steps_populated():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    scores = {u.unit_id: 0.8 for u in units}
    report = ProgressionTracker().compute(units, scores)
    assert len(report.steps) == 8


def test_compute_step_counts():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10)
    scores = {u.unit_id: 0.9 for u in units}
    report = ProgressionTracker().compute(units, scores)
    step = report.steps[0]
    assert step.level == 1
    assert step.total == 10
    assert step.completed == 10  # all above 0.7 threshold


def test_next_recommended_level_when_below_threshold():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    # Level 3 units get low score
    scores = {}
    for u in units:
        scores[u.unit_id] = 0.3 if u.level == 3 else 0.9
    report = ProgressionTracker().compute(units, scores)
    assert report.next_recommended_level == 3


def test_next_recommended_level_none_when_all_pass():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    scores = {u.unit_id: 0.9 for u in units}
    report = ProgressionTracker().compute(units, scores)
    assert report.next_recommended_level is None


def test_overall_completion_between_0_and_1():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    scores = {u.unit_id: 0.8 for u in units}
    report = ProgressionTracker().compute(units, scores)
    assert 0.0 <= report.overall_completion <= 1.0


def test_to_dict_has_expected_keys():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 3)
    scores = {u.unit_id: 0.7 for u in units}
    report = ProgressionTracker().compute(units, scores)
    d = report.to_dict()
    assert "steps" in d
    assert "overall_completion" in d
    assert "next_recommended_level" in d


def test_step_to_dict():
    step = ProgressionStep(level=1, completed=4, total=5, score=0.8)
    d = step.to_dict()
    assert d["level"] == 1
    assert d["completed"] == 4
    assert d["total"] == 5
    assert d["completion_ratio"] == pytest.approx(0.8)
