"""Tests for Phase 8.3 MushtaqDerivationEngine."""
import pytest
from mcd.concept_geometry.mushtaq_derivation_engine import MushtaqDerivationEngine
from mcd.concept_geometry.mushtaq_schema import DerivationType, ProjectedRelation


def test_katib_ism_faail():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كاتب")
    assert mu.derivation_type == DerivationType.ISM_FAAIL
    assert mu.projected_relation == ProjectedRelation.AGENT_OF
    assert mu.root == "ك ت ب"


def test_maktub_ism_mafool():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("مكتوب")
    assert mu.derivation_type == DerivationType.ISM_MAFOOL
    assert mu.projected_relation == ProjectedRelation.PATIENT_OF


def test_maktab_context_required():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("مكتب")
    assert mu.certainty_policy == "context_required"
    assert len(mu.candidate_relations) > 0


def test_kitaba_masdar():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كتابة")
    assert mu.derivation_type == DerivationType.MASDAR


def test_ziraai_nisba():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("زراعي")
    assert mu.derivation_type == DerivationType.NISBA
    assert mu.projected_relation == ProjectedRelation.ATTRIBUTED_TO


def test_unknown_word_context_required():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كلمة_غير_موجودة")
    assert mu.certainty_policy == "context_required"
    assert mu.derivation_type == DerivationType.UNKNOWN


def test_hard_rules_enforced():
    engine = MushtaqDerivationEngine()
    for word in ["كاتب", "مكتوب", "زراعة", "كلمة_غير_موجودة"]:
        mu = engine.analyze(word)
        assert mu.can_create_evidence is False
        assert mu.can_issue_certificate is False
        assert mu.can_prove_event_occurred is False


def test_zari_agent():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("زارع")
    assert mu.derivation_type == DerivationType.ISM_FAAIL
    assert mu.projected_relation == ProjectedRelation.AGENT_OF


def test_build_mushtaq_unit():
    engine = MushtaqDerivationEngine()
    mu = engine.build_mushtaq_unit("قارئ", "ق ر أ", "فاعل", DerivationType.ISM_FAAIL, "قراءة")
    assert mu.surface == "قارئ"
    assert mu.can_create_evidence is False
