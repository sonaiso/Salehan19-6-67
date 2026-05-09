"""Tests for dataset_splits.py"""
import pytest
from mcd.evaluation.dataset_splits import split_dataset, DatasetSplits
from mcd.evaluation.dataset_schema import BenchmarkExample


def _make_examples(n: int, source_type: str = "static_gold"):
    return [
        BenchmarkExample(
            example_id=f"{source_type.upper()[:3]}-{i:03d}",
            input_text=f"example {i}",
            source_type=source_type,
        )
        for i in range(n)
    ]


def test_split_basic():
    examples = _make_examples(100)
    splits = split_dataset(examples)
    assert splits.total == 100
    assert len(splits.train_calibration) > 0
    assert len(splits.validation) > 0


def test_split_ratios():
    examples = _make_examples(100)
    splits = split_dataset(examples, train_ratio=0.60, val_ratio=0.20)
    # Allow some rounding tolerance
    assert 50 <= len(splits.train_calibration) <= 70
    assert 10 <= len(splits.validation) <= 30


def test_split_total_preserved():
    examples = _make_examples(50)
    splits = split_dataset(examples)
    assert splits.total == 50


def test_split_small_dataset():
    examples = _make_examples(2)
    splits = split_dataset(examples)
    assert splits.total == 2


def test_split_to_dict():
    examples = _make_examples(30)
    splits = split_dataset(examples)
    d = splits.to_dict()
    assert "train_calibration" in d
    assert "validation" in d
    assert "holdout" in d
    assert "total" in d
    assert d["total"] == 30


def test_split_reproducible():
    examples = _make_examples(50)
    splits1 = split_dataset(examples, seed=42)
    splits2 = split_dataset(examples, seed=42)
    ids1 = [ex.example_id for ex in splits1.train_calibration]
    ids2 = [ex.example_id for ex in splits2.train_calibration]
    assert ids1 == ids2


def test_split_different_seeds_different_results():
    examples = _make_examples(50)
    splits1 = split_dataset(examples, seed=42)
    splits2 = split_dataset(examples, seed=99)
    ids1 = [ex.example_id for ex in splits1.train_calibration]
    ids2 = [ex.example_id for ex in splits2.train_calibration]
    assert ids1 != ids2


def test_split_stratified_by_source():
    examples = _make_examples(30, "static_gold") + _make_examples(20, "adversarial")
    splits = split_dataset(examples)
    train_sources = {ex.source_type for ex in splits.train_calibration}
    assert "static_gold" in train_sources
    assert "adversarial" in train_sources
