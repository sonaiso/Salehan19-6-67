"""Tests for benchmark dataset."""
from mcd.evaluation.benchmark_dataset import load_benchmark_examples, BenchmarkExample


def test_benchmark_has_50_examples():
    examples = load_benchmark_examples()
    assert len(examples) == 50


def test_benchmark_has_fire_example():
    examples = load_benchmark_examples()
    texts = [e.input_text for e in examples]
    assert any("النار" in t for t in texts)


def test_benchmark_has_lie_shari_example():
    examples = load_benchmark_examples()
    texts = [e.input_text for e in examples]
    assert any("حرام" in t for t in texts)


def test_benchmark_has_api_example():
    examples = load_benchmark_examples()
    texts = [e.input_text for e in examples]
    assert any("API" in t or "api" in t.lower() for t in texts)


def test_benchmark_has_knowledge_ambiguity():
    examples = load_benchmark_examples()
    ids = [e.example_id for e in examples]
    assert "BM-02" in ids  # علم — ambiguous


def test_benchmark_all_have_expected_behavior():
    examples = load_benchmark_examples()
    for ex in examples:
        assert isinstance(ex.expected_behavior, dict)
        assert len(ex.expected_behavior) > 0, f"Empty expected_behavior for {ex.example_id}"


def test_benchmark_example_ids_unique():
    examples = load_benchmark_examples()
    ids = [e.example_id for e in examples]
    assert len(ids) == len(set(ids))


def test_benchmark_all_have_input_text():
    examples = load_benchmark_examples()
    for ex in examples:
        assert ex.input_text.strip(), f"Empty input_text for {ex.example_id}"
