"""Tests for NisbahFrameBuilder."""
import pytest
from mcd.grounding.role_frame import RoleFrameBuilder
from mcd.grounding.nisbah_frame import NisbahFrameBuilder, NisbahType


@pytest.fixture
def builder():
    return RoleFrameBuilder()


@pytest.fixture
def nisbah_builder():
    return NisbahFrameBuilder()


def test_kataba_five_nisbah_frames(builder, nisbah_builder):
    """كتب زيد الدرس بالقلم في المدرسة أمس → 5 NisbahFrames"""
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    # Should have at least agent_of, patient_of, instrument_of, place_of, time_of
    assert len(nisbah_frames) >= 5


def test_kataba_agent_of(builder, nisbah_builder):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    types = [f.relation_type for f in nisbah_frames]
    assert NisbahType.AGENT_OF in types


def test_kataba_patient_of(builder, nisbah_builder):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    types = [f.relation_type for f in nisbah_frames]
    assert NisbahType.PATIENT_OF in types


def test_kataba_instrument_of(builder, nisbah_builder):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    types = [f.relation_type for f in nisbah_frames]
    assert NisbahType.INSTRUMENT_OF in types


def test_kataba_place_of(builder, nisbah_builder):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    types = [f.relation_type for f in nisbah_frames]
    assert NisbahType.PLACE_OF in types


def test_kataba_time_of(builder, nisbah_builder):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    types = [f.relation_type for f in nisbah_frames]
    assert NisbahType.TIME_OF in types


def test_nisbah_frame_has_source_target(builder, nisbah_builder):
    text = "كتب زيد الدرس"
    role_frame = builder.build(text)
    nisbah_frames = nisbah_builder.build(role_frame)
    for f in nisbah_frames:
        assert f.source
        assert f.target
        assert f.nisbah_id
