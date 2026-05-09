"""Tests for CertaintyPolicyClassifier."""
import pytest

from mcd.classification.certainty_policy_classifier import CertaintyPolicyClassifier
from mcd.classification.taxonomy import CertaintyPolicy, EvidenceNeed, JudgmentType


def _clf():
    return CertaintyPolicyClassifier()


def test_shari_without_evidence_suspends():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.90},
        evidence_needs={EvidenceNeed.SHARI: 0.90, EvidenceNeed.TEXTUAL: 0.80},
        knowledge_categories={},
        has_shari_evidence=False,
    )
    assert result.policy == CertaintyPolicy.SUSPEND


def test_shari_with_evidence_does_not_auto_suspend():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.90},
        evidence_needs={EvidenceNeed.SHARI: 0.90},
        knowledge_categories={},
        has_shari_evidence=True,
    )
    # Should not be suspended for shari reason
    assert result.policy != CertaintyPolicy.SUSPEND or "shari" not in result.reason.lower()


def test_no_context_suspends():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.5},
        evidence_needs={EvidenceNeed.CONTEXTUAL: 0.5},
        knowledge_categories={},
        context_provided=False,
    )
    assert result.policy == CertaintyPolicy.SUSPEND


def test_technical_returns_strong_knowledge():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.TECHNICAL: 0.90, JudgmentType.PRACTICAL: 0.60},
        evidence_needs={EvidenceNeed.TECHNICAL: 0.85},
        knowledge_categories={"technology": 0.80},
    )
    assert result.policy == CertaintyPolicy.STRONG_KNOWLEDGE


def test_science_with_sensory_strong_knowledge():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.4},
        evidence_needs={EvidenceNeed.SENSORY: 0.80, EvidenceNeed.EXPERIMENTAL: 0.70},
        knowledge_categories={"science": 0.55},
    )
    assert result.policy in (CertaintyPolicy.STRONG_KNOWLEDGE, CertaintyPolicy.NEAR_CERTAINTY)


def test_language_query_suspends():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.20},
        evidence_needs={EvidenceNeed.LINGUISTIC: 0.60, EvidenceNeed.CONTEXTUAL: 0.50},
        knowledge_categories={"language": 0.75},
    )
    assert result.policy == CertaintyPolicy.SUSPEND


def test_civilization_returns_hypothesis():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.EPISTEMIC: 0.30},
        evidence_needs={EvidenceNeed.HISTORICAL: 0.60},
        knowledge_categories={"civilization": 0.70},
    )
    assert result.policy == CertaintyPolicy.HYPOTHESIS


def test_required_before_upgrade_populated_for_shari():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.SHARI: 0.90},
        evidence_needs={EvidenceNeed.SHARI: 0.90},
        knowledge_categories={},
        has_shari_evidence=False,
    )
    assert len(result.required_before_upgrade) > 0


def test_result_has_reason():
    clf = _clf()
    result = clf.classify(
        judgment_types={JudgmentType.TECHNICAL: 0.80},
        evidence_needs={EvidenceNeed.TECHNICAL: 0.80},
        knowledge_categories={"technology": 0.70},
    )
    assert isinstance(result.reason, str)
    assert len(result.reason) > 0
