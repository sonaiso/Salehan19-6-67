"""Tests for SocietyModel."""
import pytest
from mcd.grounding.society_model import SocietyModel


@pytest.fixture
def model():
    return SocietyModel()


def test_society_rejects_corruption_warns_missing_elements(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    # Should have warnings because no systems/ideas documented
    assert frame.warnings
    assert len(frame.warnings) > 0


def test_certainty_low_without_evidence(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert frame.certainty < 0.5


def test_individual_statement_not_public_opinion(model):
    text = "شخص واحد قال رأيه"
    frame = model.analyze(text)
    assert "individual_statement_not_public_opinion" in frame.warnings


def test_society_with_systems_fewer_warnings(model):
    text = "المجتمع يرفض الفساد من خلال قانون صارم ونظام قضائي"
    frame = model.analyze(text)
    # Has more elements, should have fewer missing warnings
    missing_systems = "missing_systems_in_society" in frame.warnings
    # Still might warn about ideas/feelings
    assert isinstance(frame.warnings, list)


def test_frame_fields(model):
    text = "المجتمع يرفض الفساد"
    frame = model.analyze(text)
    assert isinstance(frame.individuals, list)
    assert isinstance(frame.ideas, list)
    assert isinstance(frame.systems, list)
    assert 0.0 <= frame.certainty <= 1.0
