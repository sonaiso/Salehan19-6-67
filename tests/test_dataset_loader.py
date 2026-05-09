"""Tests for dataset_loader.py"""
import pytest
from pathlib import Path
from mcd.evaluation.dataset_loader import (
    load_static_gold, load_adversarial, load_ambiguity,
    load_calibration, load_all, DEFAULT_DATA_DIR
)
from mcd.evaluation.dataset_schema import BenchmarkExample


def test_default_data_dir_exists():
    assert DEFAULT_DATA_DIR.exists(), f"Data dir not found: {DEFAULT_DATA_DIR}"


def test_load_static_gold():
    examples = load_static_gold()
    assert len(examples) >= 300
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "static_gold" for ex in examples)


def test_load_adversarial():
    examples = load_adversarial()
    assert len(examples) >= 50
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "adversarial" for ex in examples)


def test_load_ambiguity():
    examples = load_ambiguity()
    assert len(examples) >= 30
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "ambiguity" for ex in examples)


def test_load_calibration():
    examples = load_calibration()
    assert len(examples) >= 30
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "calibration" for ex in examples)


def test_load_all():
    examples = load_all()
    assert len(examples) >= 400
    sources = {ex.source_type for ex in examples}
    assert "static_gold" in sources
    assert "adversarial" in sources
    assert "ambiguity" in sources
    assert "calibration" in sources


def test_load_all_unique_ids():
    examples = load_all()
    ids = [ex.example_id for ex in examples]
    assert len(ids) == len(set(ids)), "Duplicate example IDs found"


def test_load_static_gold_has_all_categories():
    examples = load_static_gold()
    prefixes = {ex.example_id.split("-")[1] for ex in examples}
    expected = {"EP", "TC", "PR", "VL", "SH", "LG", "AM", "AN", "MT", "US", "CV", "SC"}
    assert expected.issubset(prefixes)
