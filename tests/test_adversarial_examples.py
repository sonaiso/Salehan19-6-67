"""Tests for adversarial_examples.py"""
import pytest
from mcd.evaluation.adversarial_examples import (
    load_adversarial_examples,
    generate_false_certainty_traps,
    generate_harm_haram_conflations,
)
from mcd.evaluation.dataset_schema import BenchmarkExample


def test_load_adversarial_examples():
    examples = load_adversarial_examples()
    assert len(examples) >= 50
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert all(ex.source_type == "adversarial" for ex in examples)


def test_generate_false_certainty_traps():
    examples = generate_false_certainty_traps(5)
    assert len(examples) == 5
    for ex in examples:
        assert ex.expected_certainty_policy == "suspend"
        assert "shari_evidence_required" in ex.required_warnings
        assert "false_certainty_detected" in ex.required_warnings
        assert "shari" in ex.expected_judgment_types
        assert ex.difficulty == "adversarial"
        assert ex.source_type == "adversarial"


def test_generate_harm_haram_conflations():
    examples = generate_harm_haram_conflations(5)
    assert len(examples) == 5
    for ex in examples:
        assert ex.expected_certainty_policy == "suspend"
        assert "harm_vs_haram" in ex.required_separations
        assert "shari_evidence_required" in ex.required_warnings
        assert ex.difficulty == "adversarial"
        assert ex.source_type == "adversarial"


def test_adversarial_ids_unique():
    fc = generate_false_certainty_traps(5)
    hh = generate_harm_haram_conflations(5)
    all_ids = [ex.example_id for ex in fc + hh]
    assert len(all_ids) == len(set(all_ids))


def test_file_adversarial_has_fc_category():
    examples = load_adversarial_examples()
    fc = [ex for ex in examples if ex.example_id.startswith("ADV-FC")]
    assert len(fc) >= 10


def test_file_adversarial_has_hh_category():
    examples = load_adversarial_examples()
    hh = [ex for ex in examples if ex.example_id.startswith("ADV-HH")]
    assert len(hh) >= 10


def test_file_adversarial_has_an_category():
    examples = load_adversarial_examples()
    an = [ex for ex in examples if ex.example_id.startswith("ADV-AN")]
    assert len(an) >= 10
