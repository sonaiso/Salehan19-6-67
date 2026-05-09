"""Tests for EvidenceNeedClassifier."""
import pytest

from mcd.classification.evidence_need_classifier import EvidenceNeedClassifier
from mcd.classification.taxonomy import EvidenceNeed, JudgmentType, KnowledgeCategory


def test_science_needs_sensory_experimental():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.6},
        knowledge_categories={KnowledgeCategory.SCIENCE: 0.7},
    )
    assert EvidenceNeed.SENSORY in result or EvidenceNeed.EXPERIMENTAL in result


def test_shari_judgment_needs_shari_evidence():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.9},
        knowledge_categories={},
    )
    assert EvidenceNeed.SHARI in result
    assert result[EvidenceNeed.SHARI] >= 0.80


def test_shari_judgment_needs_textual():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.9},
        knowledge_categories={},
    )
    assert EvidenceNeed.TEXTUAL in result


def test_language_needs_linguistic():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.4},
        knowledge_categories={KnowledgeCategory.LANGUAGE: 0.85},
    )
    assert EvidenceNeed.LINGUISTIC in result


def test_technology_needs_technical():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.TECHNICAL: 1.0},
        knowledge_categories={KnowledgeCategory.TECHNOLOGY: 0.9},
    )
    assert EvidenceNeed.TECHNICAL in result
    assert result[EvidenceNeed.TECHNICAL] >= 0.70


def test_concept_hints_override():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={},
        knowledge_categories={},
        concept_evidence_hints={EvidenceNeed.SENSORY: 0.90},
    )
    assert result.get(EvidenceNeed.SENSORY, 0.0) >= 0.85


def test_empty_inputs_returns_default():
    clf = EvidenceNeedClassifier()
    result = clf.classify(judgment_types={}, knowledge_categories={})
    assert len(result) >= 1


def test_multi_label_evidence():
    """Multiple evidence types may be required simultaneously."""
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.9},
        knowledge_categories={KnowledgeCategory.SCIENCE: 0.5},
    )
    assert len(result) >= 2


def test_scores_in_range():
    clf = EvidenceNeedClassifier()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.6},
        knowledge_categories={KnowledgeCategory.SCIENCE: 0.7},
    )
    for score in result.values():
        assert 0.0 <= score <= 1.0
