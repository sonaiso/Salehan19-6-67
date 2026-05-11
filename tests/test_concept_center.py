"""Tests for Phase 8.3 ConceptCenter."""
import pytest
from mcd.concept_geometry.concept_center import ConceptCenter, build_concept_center
from mcd.concept_geometry.mushtaq_derivation_engine import MushtaqDerivationEngine
from mcd.concept_geometry.jamid_essence_ontology import JamidEssenceOntology


def test_concept_center_hard_rules():
    cc = ConceptCenter(
        concept_id="CC-test", surface_forms=["test"], root_family="x",
        can_create_evidence=True, can_issue_certificate=True,
    )
    assert cc.can_create_evidence is False
    assert cc.can_issue_certificate is False


def test_build_concept_center_ktb():
    engine = MushtaqDerivationEngine()
    mushtaq_units = [engine.analyze(w) for w in ["كاتب", "مكتوب", "كتابة", "مكتبة", "كتابي"]]
    cc = build_concept_center(
        root_family="ك ت ب",
        surface_forms=["كاتب", "مكتوب", "كتابة", "مكتبة", "كتابي"],
        mushtaq_units=mushtaq_units,
    )
    assert cc.root_family == "ك ت ب"
    assert "كاتب" in cc.agency_axis
    assert "مكتوب" in cc.patienthood_axis
    assert "كتابي" in cc.nisba_axis
    assert cc.can_create_evidence is False
    assert cc.can_issue_certificate is False


def test_concept_center_collects_not_certifies():
    cc = build_concept_center("ز ر ع", ["زارع", "مزروع"])
    assert cc.proof_refs == []
    assert cc.can_issue_certificate is False


def test_concept_center_to_dict():
    cc = build_concept_center("ع ل م", ["عالم"])
    d = cc.to_dict()
    assert d["can_create_evidence"] is False
    assert d["can_issue_certificate"] is False
    assert d["root_family"] == "ع ل م"


def test_build_with_jamid_and_mushtaq():
    ont = JamidEssenceOntology()
    engine = MushtaqDerivationEngine()
    je = ont.get_by_surface("إنسان")
    mu = engine.analyze("عالم")
    cc = build_concept_center(
        "ع ل م",
        ["عالم"],
        jamid_essences=[je] if je else [],
        mushtaq_units=[mu],
    )
    assert cc.can_create_evidence is False
    if je:
        assert "living" in cc.essence_axis or len(cc.jamid_essence_refs) > 0


def test_concept_center_agency_axis():
    engine = MushtaqDerivationEngine()
    mu_agent = engine.analyze("كاتب")
    cc = build_concept_center("ك ت ب", ["كاتب"], mushtaq_units=[mu_agent])
    assert "كاتب" in cc.agency_axis
