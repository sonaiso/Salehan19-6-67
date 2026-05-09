"""Tests for dataset_schema.py"""
import pytest
from mcd.evaluation.dataset_schema import BenchmarkExample


def test_benchmark_example_defaults():
    ex = BenchmarkExample(example_id="TEST-001", input_text="النار تحرق")
    assert ex.language == "ar"
    assert ex.source_type == "static_gold"
    assert ex.expected_certainty_policy == "suspend"
    assert ex.expected_epistemic_status == "suspended"
    assert ex.difficulty == "medium"
    assert ex.tags == []
    assert ex.metadata == {}


def test_benchmark_example_to_dict():
    ex = BenchmarkExample(
        example_id="TEST-002",
        input_text="الماء يغلي",
        expected_certainty_policy="strong_knowledge",
        expected_epistemic_status="verified",
        tags=["epistemic"],
    )
    d = ex.to_dict()
    assert d["example_id"] == "TEST-002"
    assert d["input_text"] == "الماء يغلي"
    assert d["expected_certainty_policy"] == "strong_knowledge"
    assert d["tags"] == ["epistemic"]


def test_benchmark_example_from_dict():
    data = {
        "example_id": "TEST-003",
        "input_text": "هل الكذب حرام؟",
        "language": "ar",
        "source_type": "static_gold",
        "expected_root_domains": {"shari": 0.9},
        "expected_concept_types": {},
        "expected_knowledge_categories": {},
        "expected_judgment_types": {"shari": 0.9},
        "expected_evidence_needs": {"shari_textual": 0.9},
        "expected_certainty_policy": "suspend",
        "expected_epistemic_status": "suspended",
        "required_warnings": ["shari_evidence_required"],
        "forbidden_outputs": [],
        "required_separations": [],
        "notes": "test",
        "difficulty": "hard",
        "tags": ["shari"],
        "metadata": {},
    }
    ex = BenchmarkExample.from_dict(data)
    assert ex.example_id == "TEST-003"
    assert ex.expected_certainty_policy == "suspend"
    assert "shari_evidence_required" in ex.required_warnings


def test_benchmark_example_roundtrip():
    ex = BenchmarkExample(
        example_id="TEST-RT-001",
        input_text="علم",
        source_type="ambiguity",
        expected_certainty_policy="suspend",
        expected_epistemic_status="requires_context",
        required_warnings=["ambiguity_detected"],
        tags=["ambiguous"],
        difficulty="medium",
    )
    d = ex.to_dict()
    restored = BenchmarkExample.from_dict(d)
    assert restored.example_id == ex.example_id
    assert restored.expected_certainty_policy == ex.expected_certainty_policy
    assert restored.required_warnings == ex.required_warnings


def test_from_dict_ignores_unknown_fields():
    data = {
        "example_id": "TEST-004",
        "input_text": "test",
        "unknown_field": "should_be_ignored",
    }
    ex = BenchmarkExample.from_dict(data)
    assert ex.example_id == "TEST-004"
    assert not hasattr(ex, "unknown_field")
