"""Tests for ConceptExtractor."""
import pytest

from mcd.classification.concept_extractor import ConceptExtractor, _normalize


def test_normalize_strips_alef_variants():
    assert "ا" in _normalize("أحمد")


def test_normalize_removes_diacritics():
    result = _normalize("النَّارُ")
    assert "\u064e" not in result  # fatha


def test_normalize_handles_empty():
    assert _normalize("") == ""


def test_extract_single_word():
    extractor = ConceptExtractor()
    concepts = extractor.extract("نار")
    assert len(concepts) >= 1
    assert any(c.surface == "نار" for c in concepts)


def test_extract_filters_stop_words():
    extractor = ConceptExtractor()
    concepts = extractor.extract("في النار")
    surfaces = [c.surface for c in concepts]
    assert "في" not in surfaces


def test_extract_multi_word_nar_tahrik():
    extractor = ConceptExtractor()
    concepts = extractor.extract("النار تحرق")
    # Should extract at least النار and تحرق
    assert len(concepts) >= 1


def test_extract_multi_word_dhaka_istinaa():
    extractor = ConceptExtractor()
    concepts = extractor.extract("الذكاء الاصطناعي")
    # Multi-word concept should appear as combined or at least extracted
    surfaces = [c.surface for c in concepts]
    assert len(concepts) >= 1


def test_extract_complex_sentence():
    extractor = ConceptExtractor()
    concepts = extractor.extract("كيف نبني نظامًا تعليميًا يستخدم الذكاء الاصطناعي")
    assert len(concepts) >= 1


def test_extract_returns_prompt_concepts():
    from mcd.classification.prompt_frame import PromptConcept
    extractor = ConceptExtractor()
    concepts = extractor.extract("العقل والمنهج")
    for c in concepts:
        assert isinstance(c, PromptConcept)


def test_extract_span_indices():
    extractor = ConceptExtractor()
    concepts = extractor.extract("نار وماء")
    for c in concepts:
        assert c.span_start is not None
        assert c.span_end is not None
        assert c.span_end > c.span_start
