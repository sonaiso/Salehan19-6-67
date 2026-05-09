"""Tests for calibration_dataset.py"""
import pytest
from mcd.evaluation.calibration_dataset import (
    load_calibration_examples,
    get_calibration_by_dimension,
    get_shari_calibration,
    get_ambiguity_calibration,
    get_epistemic_calibration,
)
from mcd.evaluation.dataset_schema import BenchmarkExample


def test_load_calibration_examples():
    examples = load_calibration_examples()
    assert len(examples) >= 30
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "calibration" for ex in examples)


def test_get_calibration_by_dimension_shari():
    examples = load_calibration_examples()
    shari = get_calibration_by_dimension(examples, "shari")
    assert len(shari) > 0
    assert all("shari" in ex.tags for ex in shari)


def test_get_shari_calibration():
    examples = load_calibration_examples()
    shari = get_shari_calibration(examples)
    assert len(shari) > 0


def test_get_ambiguity_calibration():
    examples = load_calibration_examples()
    ambig = get_ambiguity_calibration(examples)
    assert len(ambig) > 0


def test_get_epistemic_calibration():
    examples = load_calibration_examples()
    epistemic = get_epistemic_calibration(examples)
    assert len(epistemic) > 0


def test_calibration_near_certainty_exists():
    """Calibration dataset must contain near_certainty policy examples."""
    examples = load_calibration_examples()
    nc = [ex for ex in examples if ex.expected_certainty_policy == "near_certainty"]
    assert len(nc) >= 1, "No near_certainty examples in calibration dataset"


def test_calibration_dimensions_covered():
    examples = load_calibration_examples()
    dimensions = set()
    for ex in examples:
        dimensions.update(ex.tags)
    expected_dims = {"shari", "epistemic", "technical", "value", "practical", "analogy", "metaphor", "usuli"}
    for d in expected_dims:
        assert d in dimensions, f"Missing calibration dimension: {d}"
