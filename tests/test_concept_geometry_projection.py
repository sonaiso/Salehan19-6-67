"""Tests for Phase 8.3 ConceptGeometryProjection."""
import pytest
from mcd.concept_geometry.concept_geometry_projection import (
    ConceptGeometryProjection, KernelProjection, CONCEPT_GEOMETRY_CONTRACT
)
from mcd.concept_geometry.jamid_essence_ontology import JamidEssenceOntology
from mcd.concept_geometry.mushtaq_derivation_engine import MushtaqDerivationEngine
from mcd.concept_geometry.concept_center import build_concept_center


def test_concept_geometry_contract():
    assert CONCEPT_GEOMETRY_CONTRACT.can_create_evidence is False
    assert CONCEPT_GEOMETRY_CONTRACT.can_issue_certificate is False
    assert "certificate" in CONCEPT_GEOMETRY_CONTRACT.forbidden_outputs
    assert "evidence" in CONCEPT_GEOMETRY_CONTRACT.forbidden_outputs


def test_projection_hard_rules():
    proj = ConceptGeometryProjection()
    assert proj.can_create_evidence is False
    assert proj.can_issue_certificate is False
    assert proj.can_form_concept is True


def test_jamid_to_projection():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("إنسان")
    proj = ConceptGeometryProjection()
    kp = proj.jamid_to_projection(je)
    assert kp.can_create_evidence is False
    assert kp.can_issue_certificate is False
    assert kp.source_layer == "concept_geometry"
    assert kp.projection_type == "essence_projection"


def test_mushtaq_to_projection():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كاتب")
    proj = ConceptGeometryProjection()
    kp = proj.mushtaq_to_projection(mu)
    assert kp.can_create_evidence is False
    assert kp.can_issue_certificate is False
    assert kp.source_layer == "concept_geometry"
    assert kp.projection_type == "derivational_projection"


def test_concept_center_to_projection():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كاتب")
    cc = build_concept_center("ك ت ب", ["كاتب"], mushtaq_units=[mu])
    proj = ConceptGeometryProjection()
    kp = proj.concept_center_to_projection(cc)
    assert kp.projection_type == "concept_formation"
    assert kp.can_create_evidence is False


def test_validate_against_contract_passes():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كاتب")
    proj = ConceptGeometryProjection()
    kp = proj.mushtaq_to_projection(mu)
    result = proj.validate_against_contract(kp)
    assert result["passed"] is True
    assert len(result["violations"]) == 0


def test_concept_geometry_projection_cannot_certificate():
    proj = ConceptGeometryProjection()
    assert proj.can_issue_certificate is False
    assert CONCEPT_GEOMETRY_CONTRACT.can_issue_certificate is False


def test_kernel_projection_hard_rules():
    kp = KernelProjection(
        projection_id="KP-test", source_layer="concept_geometry",
        projection_type="concept_formation", surface="test",
        can_create_evidence=True, can_issue_certificate=True,
    )
    assert kp.can_create_evidence is False
    assert kp.can_issue_certificate is False
