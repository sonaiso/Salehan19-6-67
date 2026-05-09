"""Tests for AdversarialCurriculum."""
from mcd.curriculum.adversarial_curriculum import (
    AdversarialExample, load_adversarial_examples, ADVERSARIAL_CATEGORIES,
)

def test_categories_nonempty(): assert len(ADVERSARIAL_CATEGORIES) >= 14
def test_load_returns_list():
    examples = load_adversarial_examples()
    assert isinstance(examples, list)
def test_at_least_200_examples():
    assert len(load_adversarial_examples()) >= 200
def test_all_are_adversarial_examples():
    for ex in load_adversarial_examples():
        assert isinstance(ex, AdversarialExample)
def test_example_has_id():
    ex = load_adversarial_examples()[0]
    assert ex.example_id.startswith("ADV-")
def test_category_in_valid_categories():
    for ex in load_adversarial_examples():
        assert ex.adversarial_category in ADVERSARIAL_CATEGORIES
def test_to_dict_has_keys():
    ex = load_adversarial_examples()[0]
    d = ex.to_dict()
    for k in ("example_id", "adversarial_category", "expected_detection"):
        assert k in d
