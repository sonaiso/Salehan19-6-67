"""Tests for PublicOpinionModel."""
import pytest
from mcd.grounding.public_opinion_model import PublicOpinionModel


@pytest.fixture
def model():
    return PublicOpinionModel()


def test_society_rejects_corruption(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert frame.idea
    assert "رفض" in frame.emotion or frame.emotion == "رفض"


def test_low_certainty_without_evidence(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert frame.certainty < 0.5


def test_no_systemic_support_warning(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert "no_systemic_support" in frame.warnings


def test_certainty_stays_low(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert frame.certainty < 0.5  # low without systemic support


def test_frame_fields(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert isinstance(frame.supporting_systems, list)
    assert isinstance(frame.opposing_systems, list)
    assert isinstance(frame.evidence, list)
    assert isinstance(frame.warnings, list)


def test_acceptance_emotion_detected(model):
    text = "الناس يقبلون العدل"
    frame = model.analyze(text)
    assert frame.emotion == "قبول" or "قبول" in frame.emotion
