"""Tests for coverage_matrix.py"""
import pytest
from mcd.evaluation.coverage_matrix import (
    CoverageMatrix, CoverageReport, DimensionCoverage,
    EXPECTED_JUDGMENT_TYPES, EXPECTED_DIFFICULTIES,
    EXPECTED_CERTAINTY_POLICIES, EXPECTED_SOURCE_TYPES
)
from mcd.evaluation.dataset_schema import BenchmarkExample


def _make_example(**kwargs):
    defaults = {
        "example_id": "COV-001",
        "input_text": "test",
        "expected_certainty_policy": "strong_knowledge",
        "expected_epistemic_status": "verified",
        "expected_judgment_types": {"epistemic": 0.9},
        "difficulty": "easy",
        "source_type": "static_gold",
    }
    defaults.update(kwargs)
    return BenchmarkExample(**defaults)


def test_empty_dataset_returns_zero_score():
    matrix = CoverageMatrix([])
    report = matrix.compute()
    assert report.total_examples == 0
    assert report.coverage_score == 0.0


def test_single_example_partial_coverage():
    ex = _make_example()
    matrix = CoverageMatrix([ex])
    report = matrix.compute()
    assert report.total_examples == 1
    assert 0.0 < report.coverage_score <= 1.0


def test_dimension_coverage_ratio():
    dc = DimensionCoverage("test", {"a", "b"}, {"a", "b", "c"})
    assert abs(dc.coverage_ratio - 2/3) < 1e-6


def test_full_coverage():
    all_jt = EXPECTED_JUDGMENT_TYPES
    all_diff = EXPECTED_DIFFICULTIES
    all_policies = EXPECTED_CERTAINTY_POLICIES
    all_sources = EXPECTED_SOURCE_TYPES

    examples = []
    for i, (jt, diff, policy, source) in enumerate(zip(all_jt, all_diff, all_policies, all_sources)):
        status = "requires_context" if jt == "ambiguous" else ("verified" if policy in ("near_certainty", "strong_knowledge") else "probable")
        if policy == "suspend":
            status = "requires_context" if jt == "ambiguous" else "suspended"
        if policy == "hypothesis":
            status = "hypothesis"
        examples.append(BenchmarkExample(
            example_id=f"FC-{i:03d}",
            input_text=f"example {i}",
            expected_judgment_types={jt: 0.9},
            difficulty=diff,
            expected_certainty_policy=policy,
            expected_epistemic_status=status,
            source_type=source,
        ))

    matrix = CoverageMatrix(examples)
    report = matrix.compute()
    assert report.coverage_score > 0.0


def test_coverage_report_to_dict():
    ex = _make_example()
    matrix = CoverageMatrix([ex])
    report = matrix.compute()
    d = report.to_dict()
    assert "total_examples" in d
    assert "coverage_score" in d
    assert "dimensions" in d
    assert len(d["dimensions"]) == 4


def test_dimension_coverage_to_dict():
    dc = DimensionCoverage("judgment_type", {"epistemic"}, EXPECTED_JUDGMENT_TYPES)
    d = dc.to_dict()
    assert d["dimension"] == "judgment_type"
    assert "covered" in d
    assert "expected" in d
    assert "coverage_ratio" in d


def test_coverage_matrix_full_dataset():
    """Full dataset must achieve >= 0.80 coverage score."""
    from mcd.evaluation.dataset_loader import load_all
    examples = load_all()
    matrix = CoverageMatrix(examples)
    report = matrix.compute()
    assert report.coverage_score >= 0.80, (
        f"Coverage score {report.coverage_score:.4f} < 0.80. "
        f"Dimensions: {[(d.dimension, d.coverage_ratio) for d in report.dimension_coverages]}"
    )
