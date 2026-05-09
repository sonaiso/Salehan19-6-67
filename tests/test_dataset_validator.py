"""Tests for dataset_validator.py"""
import pytest
from mcd.evaluation.dataset_schema import BenchmarkExample
from mcd.evaluation.dataset_validator import (
    validate_dataset, DatasetValidationReport, ValidationError,
    VALID_CERTAINTY_POLICIES, VALID_DIFFICULTIES, VALID_EPISTEMIC_STATUSES
)


def _make_example(**kwargs):
    defaults = {
        "example_id": "TEST-001",
        "input_text": "النار تحرق",
        "expected_certainty_policy": "strong_knowledge",
        "expected_epistemic_status": "verified",
        "expected_judgment_types": {"epistemic": 0.9},
        "difficulty": "easy",
        "tags": ["epistemic"],
    }
    defaults.update(kwargs)
    return BenchmarkExample(**defaults)


def test_validate_empty_dataset():
    report = validate_dataset([])
    assert report.total == 0
    assert report.valid == 0
    assert report.is_valid


def test_validate_valid_example():
    examples = [_make_example()]
    report = validate_dataset(examples)
    assert report.total == 1
    assert report.error_count == 0
    assert report.is_valid


def test_detect_duplicate_ids():
    ex1 = _make_example(example_id="DUP-001")
    ex2 = _make_example(example_id="DUP-001")
    report = validate_dataset([ex1, ex2])
    assert report.error_count >= 1
    assert any(e.field == "example_id" for e in report.errors)


def test_detect_empty_input_text():
    ex = _make_example(input_text="  ")
    report = validate_dataset([ex])
    assert report.error_count >= 1
    assert any(e.field == "input_text" for e in report.errors)


def test_detect_invalid_certainty_policy():
    ex = _make_example(expected_certainty_policy="invalid_policy")
    report = validate_dataset([ex])
    assert report.error_count >= 1
    assert any(e.field == "expected_certainty_policy" for e in report.errors)


def test_detect_invalid_difficulty():
    ex = _make_example(difficulty="extreme")
    report = validate_dataset([ex])
    assert report.error_count >= 1
    assert any(e.field == "difficulty" for e in report.errors)


def test_detect_invalid_epistemic_status():
    ex = _make_example(expected_epistemic_status="unknown_status")
    report = validate_dataset([ex])
    assert report.error_count >= 1
    assert any(e.field == "expected_epistemic_status" for e in report.errors)


def test_ambiguous_must_be_suspend():
    ex = _make_example(
        expected_judgment_types={"ambiguous": 0.9},
        expected_certainty_policy="strong_knowledge",
        expected_epistemic_status="verified",
    )
    report = validate_dataset([ex])
    assert report.error_count >= 1
    assert any(e.field == "expected_certainty_policy" for e in report.errors)


def test_to_dict_structure():
    examples = [_make_example()]
    report = validate_dataset(examples)
    d = report.to_dict()
    assert "total" in d
    assert "valid" in d
    assert "is_valid" in d
    assert "error_count" in d
    assert "errors" in d
    assert "warnings" in d


def test_validate_real_dataset():
    from mcd.evaluation.dataset_loader import load_all
    examples = load_all()
    report = validate_dataset(examples)
    assert report.total >= 400
    assert report.is_valid, f"Dataset has errors: {report.errors[:3]}"
