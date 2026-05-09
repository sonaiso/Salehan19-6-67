"""Tests for AdvancedArabicUsulSemantics."""
import pytest
from mcd.grounding.usul_semantics import (
    AdvancedArabicUsulSemantics,
    DalalahType,
    GeneralityLevel,
    IltizamType,
    TruthMetaphor,
)


@pytest.fixture
def semantics():
    return AdvancedArabicUsulSemantics()


def test_qiyas_without_illah_warning(semantics):
    frame = semantics.analyze(
        dal="الخمر",
        madlul="محرم",
        qiyas_requested=True,
        illah=None,
    )
    assert "qiyas_without_illah" in frame.warnings
    assert frame.qiyas_candidate is False


def test_qiyas_with_illah_no_warning(semantics):
    frame = semantics.analyze(
        dal="الخمر",
        madlul="محرم",
        qiyas_requested=True,
        illah="الإسكار",
    )
    assert "qiyas_without_illah" not in frame.warnings
    assert frame.qiyas_candidate is True


def test_iltizam_metaphorical_weak_evidence(semantics):
    frame = semantics.analyze(
        dal="الأسد",
        madlul="الشجاع",
        dalalah_type=DalalahType.ILTIZAM,
        iltizam_type=IltizamType.METAPHORICAL,
    )
    assert "weak_iltizam_evidence" in frame.warnings
    assert frame.certainty < 0.6


def test_iltizam_logical_strong_evidence(semantics):
    frame = semantics.analyze(
        dal="الاثنان",
        madlul="زوج",
        dalalah_type=DalalahType.ILTIZAM,
        iltizam_type=IltizamType.LOGICAL,
    )
    assert "weak_iltizam_evidence" not in frame.warnings
    assert frame.certainty >= 0.7


def test_aam_with_restriction_becomes_khas(semantics):
    frame = semantics.analyze(
        dal="الناس",
        madlul="مكلفون",
        generality=GeneralityLevel.AAM,
        restriction="إلا_المجانين",
    )
    assert frame.generality == GeneralityLevel.KHAS
    assert "aam_restricted_to_khas" in frame.warnings


def test_mutlaq_with_restriction_becomes_muqayyad(semantics):
    frame = semantics.analyze(
        dal="الرقبة",
        madlul="العتق",
        generality=GeneralityLevel.MUTLAQ,
        restriction="مؤمنة",
    )
    from mcd.grounding.usul_semantics import GeneralityLevel as GL
    assert frame.generality == GL.MUQAYYAD


def test_majaz_lowers_certainty(semantics):
    frame_haqiqa = semantics.analyze(dal="ماء", madlul="مادة سائلة")
    frame_majaz = semantics.analyze(
        dal="ماء",
        madlul="مادة سائلة",
        truth_or_metaphor=TruthMetaphor.MAJAZ,
    )
    assert frame_majaz.certainty < frame_haqiqa.certainty


def test_frame_fields_present(semantics):
    frame = semantics.analyze(dal="نار", madlul="ظاهرة احتراق")
    assert frame.dal == "نار"
    assert frame.madlul == "ظاهرة احتراق"
    assert 0.0 <= frame.certainty <= 1.0
