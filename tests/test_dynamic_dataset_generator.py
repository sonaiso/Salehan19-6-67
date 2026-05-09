"""Tests for dynamic_dataset_generator.py"""
import pytest
from mcd.evaluation.dynamic_dataset_generator import DynamicDatasetGenerator
from mcd.evaluation.dataset_schema import BenchmarkExample


@pytest.fixture
def gen():
    return DynamicDatasetGenerator(seed=42)


def test_generator_loads_templates(gen):
    assert len(gen.templates) >= 10


def test_generate_from_templates(gen):
    examples = gen.generate_from_templates(gen.templates, 20)
    assert len(examples) <= 20
    assert len(examples) > 0
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)


def test_generate_profile(gen):
    examples = gen.generate_profile("standard", 50)
    assert len(examples) > 0
    assert all(ex.source_type == "dynamic_generated" for ex in examples)


def test_generate_balanced(gen):
    examples = gen.generate_balanced(count_per_category=2)
    assert len(examples) > 0
    assert all(ex.source_type == "dynamic_generated" for ex in examples)


def test_generate_adversarial(gen):
    examples = gen.generate_adversarial(10)
    assert len(examples) > 0


def test_generated_examples_have_valid_fields(gen):
    examples = gen.generate_from_templates(gen.templates, 30)
    for ex in examples:
        assert ex.example_id
        assert ex.input_text
        assert ex.language == "ar"
        assert ex.source_type == "dynamic_generated"
        assert ex.expected_certainty_policy in {
            "near_certainty", "strong_knowledge", "probable_knowledge", "hypothesis", "suspend"
        }


def test_generated_shari_examples_suspend(gen):
    haram_templates = [t for t in gen.templates if "HARM" in t["template_id"]]
    if haram_templates:
        examples = gen.generate_from_templates(haram_templates, 5)
        for ex in examples:
            assert ex.expected_certainty_policy == "suspend"


def test_generated_ambiguous_examples(gen):
    ambig_templates = [t for t in gen.templates if "AMBIG" in t["template_id"]]
    if ambig_templates:
        examples = gen.generate_from_templates(ambig_templates, 5)
        for ex in examples:
            assert ex.expected_certainty_policy == "suspend"
            assert ex.expected_epistemic_status == "requires_context"


def test_expand_template_variable_substitution(gen):
    tmpl = gen.templates[0]
    ex = gen._expand_template(tmpl, 0)
    variables = tmpl.get("variables", {})
    for var, values in variables.items():
        assert f"{{{var}}}" not in ex.input_text


def test_generate_max_examples_respected(gen):
    examples = gen.generate_from_templates(gen.templates, 5)
    assert len(examples) <= 5
