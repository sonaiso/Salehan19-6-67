"""Tests for Router."""
import pytest

from mcd.classification.router import Router, RoutingDecision
from mcd.classification.taxonomy import CertaintyPolicy, EvidenceNeed, JudgmentType, KnowledgeCategory


def _router():
    return Router()


def test_shari_suspend_routes_to_nabhani():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.SHARI: 0.90},
        knowledge_categories={},
        evidence_needs={EvidenceNeed.SHARI: 0.90, EvidenceNeed.TEXTUAL: 0.80},
        certainty_policy=CertaintyPolicy.SUSPEND,
    )
    assert result.primary_engine == "nabhani_decoder"
    assert result.should_suspend is True


def test_epistemic_routes_to_nabhani():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.EPISTEMIC: 0.70},
        knowledge_categories={},
        evidence_needs={EvidenceNeed.SENSORY: 0.60},
        certainty_policy=CertaintyPolicy.STRONG_KNOWLEDGE,
    )
    assert result.primary_engine == "nabhani_decoder"
    assert result.should_suspend is False


def test_technical_routes_to_mcd():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.TECHNICAL: 0.90},
        knowledge_categories={KnowledgeCategory.TECHNOLOGY: 0.80},
        evidence_needs={EvidenceNeed.TECHNICAL: 0.80},
        certainty_policy=CertaintyPolicy.STRONG_KNOWLEDGE,
    )
    assert result.primary_engine == "mcd"


def test_language_routes_to_dal_madlul():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.EPISTEMIC: 0.50},
        knowledge_categories={KnowledgeCategory.LANGUAGE: 0.80},
        evidence_needs={EvidenceNeed.LINGUISTIC: 0.70},
        certainty_policy=CertaintyPolicy.STRONG_KNOWLEDGE,  # not suspend, let language rule fire
    )
    assert "dal_madlul_mapper" in result.sub_engines or "concept_grounder" in result.sub_engines


def test_result_is_routing_decision():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.EPISTEMIC: 0.50},
        knowledge_categories={},
        evidence_needs={},
        certainty_policy=CertaintyPolicy.HYPOTHESIS,
    )
    assert isinstance(result, RoutingDecision)


def test_requires_evidence_list():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.SHARI: 0.90},
        knowledge_categories={},
        evidence_needs={EvidenceNeed.SHARI: 0.90},
        certainty_policy=CertaintyPolicy.SUSPEND,
    )
    assert len(result.requires_evidence) > 0


def test_reason_is_string():
    r = _router()
    result = r.route(
        judgment_types={JudgmentType.TECHNICAL: 0.80},
        knowledge_categories={KnowledgeCategory.TECHNOLOGY: 0.80},
        evidence_needs={EvidenceNeed.TECHNICAL: 0.80},
        certainty_policy=CertaintyPolicy.STRONG_KNOWLEDGE,
    )
    assert isinstance(result.reason, str)
    assert len(result.reason) > 0
