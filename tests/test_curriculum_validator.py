"""Tests for CurriculumValidator."""
from __future__ import annotations

import pytest
from mcd.curriculum.cognitive_unit import CognitiveUnit
from mcd.curriculum.reality_frame import RealityFrame
from mcd.curriculum.curriculum_validator import CurriculumValidator, CurriculumValidationReport
from mcd.curriculum.curriculum_generator import CurriculumGenerator


def _make_valid_unit(uid: str = "CURR-L01-0001", level: int = 1) -> CognitiveUnit:
    return CognitiveUnit(
        unit_id=uid,
        input_text="النار شيء.",
        level=level,
        target_layer="thing",
        expected_frame=RealityFrame(things=["النار"], certainty_policy="certain_knowledge"),
        certainty_policy="certain_knowledge",
        difficulty="easy",
        tags=["things"],
    )


def test_valid_units_pass():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10)
    report = CurriculumValidator().validate(units)
    assert report.status == "valid"
    assert report.invalid_units == 0


def test_report_has_correct_total():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 5)
    report = CurriculumValidator().validate(units)
    assert report.total_units == 5


def test_empty_input_text_fails():
    unit = _make_valid_unit()
    unit.input_text = ""
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert report.invalid_units == 1
    assert any(e.field == "input_text" for e in report.errors)


def test_invalid_level_fails():
    unit = _make_valid_unit()
    unit.level = 99
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert any(e.field == "level" for e in report.errors)


def test_invalid_target_layer_fails():
    unit = _make_valid_unit()
    unit.target_layer = "nonexistent_layer"
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert any(e.field == "target_layer" for e in report.errors)


def test_invalid_certainty_policy_fails():
    unit = _make_valid_unit()
    unit.certainty_policy = "totally_sure"
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert any(e.field == "certainty_policy" for e in report.errors)


def test_adversarial_without_forbidden_confusions_fails():
    unit = _make_valid_unit()
    unit.difficulty = "adversarial"
    unit.forbidden_confusions = []
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert any(e.field == "forbidden_confusions" for e in report.errors)


def test_adversarial_with_forbidden_confusions_passes():
    unit = _make_valid_unit()
    unit.difficulty = "adversarial"
    unit.forbidden_confusions = ["some_confusion"]
    report = CurriculumValidator().validate([unit])
    assert report.status == "valid"


def test_duplicate_unit_id_fails():
    unit1 = _make_valid_unit("CURR-L01-0001")
    unit2 = _make_valid_unit("CURR-L01-0001")
    report = CurriculumValidator().validate([unit1, unit2])
    assert report.status == "invalid"
    assert any(e.field == "unit_id" and "Duplicate" in e.message for e in report.errors)


def test_evidence_unit_without_evidence_need_fails():
    unit = CognitiveUnit(
        unit_id="CURR-L07-0001",
        input_text="يحتاج دليل.",
        level=7,
        target_layer="evidence",
        expected_frame=RealityFrame(evidence_need=["textual"], certainty_policy="insufficient_evidence"),
        certainty_policy="insufficient_evidence",
        evidence_need=[],  # missing!
    )
    report = CurriculumValidator().validate([unit])
    assert report.status == "invalid"
    assert any(e.field == "evidence_need" for e in report.errors)


def test_to_dict_has_expected_keys():
    report = CurriculumValidationReport(total_units=5, valid_units=5, invalid_units=0, status="valid")
    d = report.to_dict()
    for key in ["total_units", "valid_units", "invalid_units", "errors", "warnings", "status"]:
        assert key in d


def test_full_curriculum_validates():
    from mcd.curriculum.curriculum_dataset import CurriculumDataset
    ds = CurriculumDataset()
    units = ds.load_all()
    report = CurriculumValidator().validate(units)
    assert report.total_units == 400
    assert report.status == "valid"
