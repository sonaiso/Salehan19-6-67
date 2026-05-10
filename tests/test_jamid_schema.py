"""Tests for Phase 8.3 JamidEssence schema."""
import pytest
from mcd.concept_geometry.jamid_schema import JamidEssence, EssenceType


def test_essence_type_enum():
    assert EssenceType.GENUS.value == "genus"
    assert EssenceType.SPECIES.value == "species"
    assert EssenceType.ABSTRACT_CONCEPT.value == "abstract_concept"


def test_jamid_essence_hard_rules():
    je = JamidEssence.make("إنسان", EssenceType.SPECIES, "حيوان", "إنسان")
    assert je.can_create_evidence is False
    assert je.can_issue_certificate is False


def test_jamid_essence_hard_rules_cannot_be_overridden():
    je = JamidEssence(
        essence_id="JE-test", surface="test", normalized="test",
        essence_type=EssenceType.UNKNOWN, genus="x", species="y",
        can_create_evidence=True, can_issue_certificate=True,
    )
    assert je.can_create_evidence is False
    assert je.can_issue_certificate is False


def test_jamid_essence_to_dict():
    je = JamidEssence.make("حجر", EssenceType.NATURAL_OBJECT, "جماد", "صخرة",
                           differentia=["صلب"])
    d = je.to_dict()
    assert d["can_create_evidence"] is False
    assert d["can_issue_certificate"] is False
    assert d["essence_type"] == "natural_object"
    assert "صلب" in d["differentia"]


def test_jamid_essence_from_dict_roundtrip():
    je = JamidEssence.make("ماء", EssenceType.MATERIAL, "مادة", "سائل",
                           differentia=["شفاف"])
    d = je.to_dict()
    je2 = JamidEssence.from_dict(d)
    assert je2.surface == je.surface
    assert je2.essence_type == je.essence_type
    assert je2.can_create_evidence is False
    assert je2.can_issue_certificate is False


def test_jamid_essence_from_dict_ignores_forbidden_flags():
    d = {
        "essence_id": "JE-test", "surface": "test", "normalized": "test",
        "essence_type": "tool", "genus": "أداة", "species": "أداة",
        "can_create_evidence": True, "can_issue_certificate": True,
    }
    je = JamidEssence.from_dict(d)
    assert je.can_create_evidence is False
    assert je.can_issue_certificate is False


def test_jamid_essence_evidence_state():
    je = JamidEssence.make("نار", EssenceType.NATURAL_OBJECT, "طاقة", "حرارة")
    assert je.evidence_state == "missing"
