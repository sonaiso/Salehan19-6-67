"""Tests for GoldenExample and load_golden_examples."""
from mcd.curriculum.golden_examples import GoldenExample, load_golden_examples

def test_load_returns_list():
    examples = load_golden_examples()
    assert isinstance(examples, list)

def test_at_least_50_examples():
    examples = load_golden_examples()
    assert len(examples) >= 50

def test_all_are_golden_examples():
    for ex in load_golden_examples():
        assert isinstance(ex, GoldenExample)

def test_golden_example_has_id():
    ex = load_golden_examples()[0]
    assert ex.example_id.startswith("GOLDEN-")

def test_golden_example_has_text():
    ex = load_golden_examples()[0]
    assert len(ex.input_text) > 0

def test_golden_example_has_domains():
    ex = load_golden_examples()[0]
    assert isinstance(ex.expected_domains, list)

def test_to_dict_has_required_keys():
    ex = load_golden_examples()[0]
    d = ex.to_dict()
    for key in ("example_id", "input_text", "certainty_policy", "expected_domains"):
        assert key in d

def test_certainty_policies_valid():
    from mcd.curriculum.curriculum_schema import VALID_CERTAINTY_POLICIES
    for ex in load_golden_examples():
        assert ex.certainty_policy in VALID_CERTAINTY_POLICIES
