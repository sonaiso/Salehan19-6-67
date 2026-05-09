"""Tests for ConceptClassifier."""
import pytest

from mcd.classification.concept_classifier import ConceptClassifier
from mcd.classification.prompt_frame import PromptConcept
from mcd.classification.taxonomy import ConceptType, KnowledgeCategory, RootDomain


def _make_concept(surface: str, normalized: str | None = None) -> PromptConcept:
    return PromptConcept(surface=surface, normalized=normalized or surface)


def test_classify_nar_root_domain():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("نار"))
    assert result.root_domain.get(RootDomain.UNIVERSE, 0.0) >= 0.8


def test_classify_nar_concept_type():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("نار"))
    assert result.concept_type.get(ConceptType.THING, 0.0) >= 0.7


def test_classify_nar_knowledge_category():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("نار"))
    assert result.knowledge_category.get(KnowledgeCategory.SCIENCE, 0.0) >= 0.5


def test_classify_aql_human_domain():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("عقل"))
    assert result.root_domain.get(RootDomain.HUMAN, 0.0) >= 0.8


def test_classify_api_tool():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("api"))
    assert result.concept_type.get(ConceptType.TOOL, 0.0) >= 0.8


def test_classify_api_technology():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("api"))
    assert result.knowledge_category.get(KnowledgeCategory.TECHNOLOGY, 0.0) >= 0.8


def test_classify_all_returns_list():
    clf = ConceptClassifier()
    concepts = [_make_concept("نار"), _make_concept("عقل")]
    results = clf.classify_all(concepts)
    assert len(results) == 2


def test_classify_al_prefixed_word():
    """Words with definite article 'ال' should be looked up correctly."""
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("النار", normalized="النار"))
    # With ال-stripping in lookup, universe score should be present
    assert result.root_domain.get(RootDomain.UNIVERSE, 0.0) >= 0.7


def test_classify_haraam_value():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("حرام"))
    assert result.concept_type.get(ConceptType.VALUE, 0.0) >= 0.7


def test_classify_preserves_surface():
    clf = ConceptClassifier()
    concept = _make_concept("نظام")
    result = clf.classify(concept)
    assert result.surface == concept.surface


def test_classify_scores_in_range():
    clf = ConceptClassifier()
    result = clf.classify(_make_concept("نار"))
    for score in result.root_domain.values():
        assert 0.0 <= score <= 1.0
    for score in result.concept_type.values():
        assert 0.0 <= score <= 1.0
