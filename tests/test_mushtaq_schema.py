"""Tests for Phase 8.3 MushtaqUnit schema."""
import pytest
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit, DerivationType, ProjectedRelation


def test_derivation_type_enum():
    assert DerivationType.ISM_FAAIL.value == "ism_faail"
    assert DerivationType.ISM_MAFOOL.value == "ism_mafool"
    assert DerivationType.MASDAR.value == "masdar"
    assert DerivationType.NISBA.value == "nisba"


def test_projected_relation_enum():
    assert ProjectedRelation.AGENT_OF.value == "agent_of"
    assert ProjectedRelation.PATIENT_OF.value == "patient_of"
    assert ProjectedRelation.INSTRUMENT_OF.value == "instrument_of"


def test_mushtaq_hard_rules():
    mu = MushtaqUnit.make("كاتب", "ك ت ب", "فاعل", DerivationType.ISM_FAAIL,
                          projected_relation=ProjectedRelation.AGENT_OF)
    assert mu.can_create_evidence is False
    assert mu.can_issue_certificate is False
    assert mu.can_prove_event_occurred is False


def test_mushtaq_hard_rules_cannot_be_overridden():
    mu = MushtaqUnit(
        mushtaq_id="MU-test", surface="test", normalized="test",
        root="", pattern="", derivation_type=DerivationType.UNKNOWN,
        can_create_evidence=True, can_issue_certificate=True, can_prove_event_occurred=True,
    )
    assert mu.can_create_evidence is False
    assert mu.can_issue_certificate is False
    assert mu.can_prove_event_occurred is False


def test_mushtaq_to_dict():
    mu = MushtaqUnit.make("كاتب", "ك ت ب", "فاعل", DerivationType.ISM_FAAIL,
                          folded_event="كتابة", projected_relation=ProjectedRelation.AGENT_OF)
    d = mu.to_dict()
    assert d["can_create_evidence"] is False
    assert d["can_issue_certificate"] is False
    assert d["can_prove_event_occurred"] is False
    assert d["derivation_type"] == "ism_faail"
    assert d["projected_relation"] == "agent_of"


def test_mushtaq_from_dict_roundtrip():
    mu = MushtaqUnit.make("مكتوب", "ك ت ب", "مفعول", DerivationType.ISM_MAFOOL,
                          projected_relation=ProjectedRelation.PATIENT_OF)
    d = mu.to_dict()
    mu2 = MushtaqUnit.from_dict(d)
    assert mu2.surface == mu.surface
    assert mu2.derivation_type == mu.derivation_type
    assert mu2.can_create_evidence is False
    assert mu2.can_prove_event_occurred is False


def test_mushtaq_from_dict_ignores_forbidden_flags():
    d = {
        "mushtaq_id": "MU-test", "surface": "test", "normalized": "test",
        "root": "ك ت ب", "pattern": "فاعل", "derivation_type": "ism_faail",
        "can_create_evidence": True, "can_issue_certificate": True, "can_prove_event_occurred": True,
    }
    mu = MushtaqUnit.from_dict(d)
    assert mu.can_create_evidence is False
    assert mu.can_issue_certificate is False
    assert mu.can_prove_event_occurred is False
