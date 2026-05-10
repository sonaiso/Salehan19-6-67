"""Tests for Phase 8.3 JamidEssenceOntology."""
import pytest
from mcd.concept_geometry.jamid_essence_ontology import JamidEssenceOntology
from mcd.concept_geometry.jamid_schema import EssenceType


def test_load_builtin_essences():
    ont = JamidEssenceOntology()
    essences = ont.all_essences()
    assert len(essences) >= 12


def test_get_insan():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("إنسان")
    assert je is not None
    assert je.genus == "حيوان"
    assert je.can_create_evidence is False
    assert je.can_issue_certificate is False


def test_get_hajar():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("حجر")
    assert je is not None
    assert je.essence_type == EssenceType.NATURAL_OBJECT


def test_get_maa():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("ماء")
    assert je is not None
    assert je.essence_type == EssenceType.MATERIAL


def test_classify_jamid():
    ont = JamidEssenceOntology()
    et = ont.classify_jamid("إنسان")
    assert et == EssenceType.SPECIES


def test_infer_essence_vector():
    ont = JamidEssenceOntology()
    vec = ont.infer_essence_vector("إنسان")
    assert "living" in vec
    assert vec["living"] == 1.0


def test_to_projection_found():
    ont = JamidEssenceOntology()
    proj = ont.to_projection("إنسان")
    assert proj["found"] is True
    assert proj["can_create_evidence"] is False
    assert proj["can_issue_certificate"] is False
    assert proj["source_layer"] == "concept_geometry"


def test_to_projection_not_found():
    ont = JamidEssenceOntology()
    proj = ont.to_projection("كلمة_غير_موجودة")
    assert proj["found"] is False
    assert proj["can_create_evidence"] is False
    assert proj["can_issue_certificate"] is False


def test_all_essences_have_no_evidence_capability():
    ont = JamidEssenceOntology()
    for je in ont.all_essences():
        assert je.can_create_evidence is False
        assert je.can_issue_certificate is False
