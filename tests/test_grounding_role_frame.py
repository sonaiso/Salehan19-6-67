"""Tests for RoleFrameBuilder."""
import pytest
from mcd.grounding.role_frame import RoleFrameBuilder


@pytest.fixture
def builder():
    return RoleFrameBuilder()


def test_kataba_full_sentence(builder):
    """كتب زيد الدرس بالقلم في المدرسة أمس"""
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    frame = builder.build(text)
    assert frame.action == "كتب"
    assert frame.agent == "زيد"
    assert frame.patient == "الدرس" or frame.patient == "درس"
    assert frame.instrument is not None and "قلم" in frame.instrument
    assert frame.place is not None and "مدرسة" in frame.place
    assert frame.time == "أمس"


def test_akala_sentence(builder):
    """أكل الولد التفاحة في البيت"""
    text = "أكل الولد التفاحة في البيت"
    frame = builder.build(text)
    assert frame.action == "أكل"
    assert frame.agent is not None and "ولد" in frame.agent
    assert frame.patient is not None and "تفاح" in frame.patient
    assert frame.place is not None and "بيت" in frame.place
    assert frame.time is None


def test_frame_has_id(builder):
    frame = builder.build("كتب زيد الكتاب")
    assert frame.frame_id
    assert frame.raw_text == "كتب زيد الكتاب"


def test_certainty_positive(builder):
    frame = builder.build("كتب زيد الدرس")
    assert frame.certainty > 0.0


def test_simple_verb_detection(builder):
    frame = builder.build("شرب زيد الماء")
    assert frame.action == "شرب"
    assert frame.agent == "زيد"
