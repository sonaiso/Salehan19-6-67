"""Tests for Phase 8.3 ConceptGeometryValidator."""
import pytest
from mcd.concept_geometry.concept_geometry_validator import ConceptGeometryValidator
from mcd.concept_geometry.jamid_schema import JamidEssence, EssenceType
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit, DerivationType, ProjectedRelation


def test_quick_validate_passes():
    validator = ConceptGeometryValidator()
    report = validator.quick_validate()
    assert report.passed is True
    assert report.concept_geometry_score >= 0.95
    assert len(report.violations) == 0


def test_concept_geometry_passes_cfk_contract():
    validator = ConceptGeometryValidator()
    report = validator.quick_validate()
    assert report.cfk_contract_score >= 0.95


def test_violation_for_can_create_evidence():
    validator = ConceptGeometryValidator()
    je = JamidEssence.make("test", EssenceType.UNKNOWN, "x", "y")
    # Manually set the flag (bypassing __post_init__ via object.__setattr__)
    object.__setattr__(je, "can_create_evidence", True)
    report = validator.validate(jamid_essences=[je])
    assert not report.passed
    assert any("can_create_evidence" in v for v in report.violations)


def test_validation_report_to_dict():
    validator = ConceptGeometryValidator()
    report = validator.quick_validate()
    d = report.to_dict()
    assert "passed" in d
    assert "concept_geometry_score" in d
    assert d["concept_geometry_score"] >= 0.95


def test_validation_report_to_markdown():
    validator = ConceptGeometryValidator()
    report = validator.quick_validate()
    md = report.to_markdown()
    assert "Phase 8.3" in md
    assert "PASSED" in md


def test_empty_inputs_pass():
    validator = ConceptGeometryValidator()
    report = validator.validate()
    assert report.passed is True


def test_mushtaq_violations_reported():
    validator = ConceptGeometryValidator()
    mu = MushtaqUnit.make("test", "x", "y", DerivationType.UNKNOWN)
    object.__setattr__(mu, "can_prove_event_occurred", True)
    report = validator.validate(mushtaq_units=[mu])
    assert not report.passed
    assert any("can_prove_event_occurred" in v for v in report.violations)
