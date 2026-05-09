"""Tests for ConceptPropagationModel."""
import pytest
from mcd.grounding.concept_propagation import (
    ConceptPropagationModel,
    ConceptPropagationFrame,
    PropagationChannel,
)


@pytest.fixture
def model():
    return ConceptPropagationModel()


def test_concept_with_channels(model):
    frame = model.analyze(
        concept="الحرية",
        channels=[PropagationChannel.MEDIA, PropagationChannel.EDUCATION],
    )
    assert isinstance(frame, ConceptPropagationFrame)
    assert frame.concept == "الحرية"
    assert len(frame.channels) == 2


def test_no_evidence_low_certainty(model):
    frame = model.analyze(concept="مفهوم_ما")
    assert frame.certainty < 0.5


def test_with_evidence_higher_certainty(model):
    frame = model.analyze(
        concept="الديمقراطية",
        evidence=["دراسة_أ", "دراسة_ب", "دراسة_ج"],
    )
    assert frame.certainty > 0.3


def test_institutional_enforcement_raises_adoption(model):
    frame = model.analyze(
        concept="القانون",
        channels=[PropagationChannel.INSTITUTIONAL_ENFORCEMENT],
    )
    assert frame.adoption_level > 0.0


def test_frame_fields(model):
    frame = model.analyze(concept="التعليم")
    assert isinstance(frame.carriers, list)
    assert isinstance(frame.channels, list)
    assert 0.0 <= frame.adoption_level <= 1.0
    assert 0.0 <= frame.resistance <= 1.0


def test_public_opinion_channel_effect(model):
    frame = model.analyze(
        concept="الرأي_العام",
        channels=[PropagationChannel.PUBLIC_OPINION],
    )
    assert frame.public_atmosphere_effect > 0.0
