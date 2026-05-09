"""Tests for CalibrationBridge."""
from __future__ import annotations

import pytest
from mcd.curriculum.calibration_bridge import CalibrationBridge, CurriculumCoverageReport
from mcd.curriculum.curriculum_generator import CurriculumGenerator
from mcd.curriculum.curriculum_dataset import CurriculumDataset


def test_export_to_evaluation_dataset():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 5)
    bridge = CalibrationBridge()
    result = bridge.export_to_evaluation_dataset(units)
    assert len(result) == 5
    for item in result:
        assert "example_id" in item
        assert "input_text" in item
        assert "judgment_type" in item
        assert item["source"] == "curriculum"


def test_export_to_calibration_cases_only_l7_l8():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    cases = bridge.export_to_calibration_cases(units)
    assert len(cases) == 10  # 5 from L7 + 5 from L8
    for case in cases:
        assert case["level"] in (7, 8)


def test_export_to_calibration_cases_has_expected_keys():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 5)
    bridge = CalibrationBridge()
    cases = bridge.export_to_calibration_cases(units)
    for case in cases:
        for key in ["unit_id", "input_text", "expected_certainty_policy", "evidence_need", "forbidden_confusions", "level"]:
            assert key in case


def test_compute_curriculum_coverage_returns_report():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage(units)
    assert isinstance(report, CurriculumCoverageReport)


def test_compute_curriculum_coverage_all_levels():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage(units)
    assert report.levels_covered == [1, 2, 3, 4, 5, 6, 7, 8]


def test_compute_curriculum_coverage_ratio_valid():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage(units)
    assert 0.0 <= report.coverage_ratio <= 1.0


def test_compute_curriculum_coverage_score_estimates():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage(units)
    assert report.dataset_score_estimate > 0.0
    assert report.calibration_score_estimate > 0.0
    assert report.industrial_testing_score_estimate > 0.0
    assert report.source_trust_score_estimate > 0.0


def test_compute_curriculum_coverage_empty():
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage([])
    assert report.total_units == 0
    assert report.coverage_ratio == 0.0


def test_produce_pre_api_improvement_metrics():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    metrics = bridge.produce_pre_api_improvement_metrics(units)
    expected_keys = [
        "curriculum_units", "coverage_ratio", "dataset_score_estimate",
        "calibration_score_estimate", "industrial_testing_score_estimate",
        "source_trust_score_estimate", "levels_covered", "layers_covered",
    ]
    for key in expected_keys:
        assert key in metrics
    assert metrics["curriculum_units"] == 40


def test_coverage_report_to_dict():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = CalibrationBridge()
    report = bridge.compute_curriculum_coverage(units)
    d = report.to_dict()
    for key in ["total_units", "levels_covered", "layers_covered", "coverage_ratio"]:
        assert key in d
