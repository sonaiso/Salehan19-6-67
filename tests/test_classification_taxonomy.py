"""Tests for FPCL taxonomy enumerations."""
import pytest

from mcd.classification.taxonomy import (
    CertaintyPolicy,
    ConceptType,
    EvidenceNeed,
    JudgmentType,
    KnowledgeCategory,
    RootDomain,
)


def test_root_domain_values():
    assert RootDomain.UNIVERSE.value == "universe"
    assert RootDomain.HUMAN.value == "human"
    assert RootDomain.LIFE.value == "life"


def test_concept_type_members():
    members = {ct.value for ct in ConceptType}
    assert "thing" in members
    assert "property" in members
    assert "relation" in members
    assert "value" in members
    assert "system" in members
    assert "tool" in members
    assert "purpose" in members


def test_knowledge_category_members():
    members = {kc.value for kc in KnowledgeCategory}
    assert "science" in members
    assert "culture" in members
    assert "civilization" in members
    assert "technology" in members
    assert "language" in members
    assert "method" in members


def test_judgment_type_members():
    members = {jt.value for jt in JudgmentType}
    assert "epistemic" in members
    assert "technical" in members
    assert "value" in members
    assert "shari" in members
    assert "practical" in members


def test_evidence_need_members():
    members = {en.value for en in EvidenceNeed}
    assert "sensory" in members
    assert "experimental" in members
    assert "linguistic" in members
    assert "textual" in members
    assert "historical" in members
    assert "shari" in members
    assert "technical" in members
    assert "contextual" in members


def test_certainty_policy_members():
    members = {cp.value for cp in CertaintyPolicy}
    assert "near_certainty" in members
    assert "strong_knowledge" in members
    assert "hypothesis" in members
    assert "suspend" in members


def test_enums_are_str_subclass():
    """All enums inherit from str for JSON compatibility."""
    assert isinstance(RootDomain.UNIVERSE, str)
    assert isinstance(ConceptType.THING, str)
    assert isinstance(KnowledgeCategory.SCIENCE, str)
    assert isinstance(JudgmentType.EPISTEMIC, str)
    assert isinstance(EvidenceNeed.SENSORY, str)
    assert isinstance(CertaintyPolicy.NEAR_CERTAINTY, str)
