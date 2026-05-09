"""Tests for HumanIndividualModel."""
import pytest
from mcd.grounding.human_individual_model import HumanIndividualModel, HumanFrame, IndividualFrame


@pytest.fixture
def model():
    return HumanIndividualModel()


def test_human_frame_represents_species(model):
    frame = model.create_human_frame()
    assert isinstance(frame, HumanFrame)
    assert frame.human_as_species == "الإنسان"
    assert frame.mind == "عاقل"


def test_individual_frame_represents_individual(model):
    frame = model.create_individual_frame(name="زيد", context="طالب")
    assert isinstance(frame, IndividualFrame)
    assert frame.name == "زيد"
    assert frame.context == "طالب"


def test_cannot_generalize_from_individual(model):
    individual = model.create_individual_frame("محمد", behavior="كريم")
    can_gen, reason = model.can_generalize_to_species(individual)
    assert can_gen is False
    assert reason


def test_human_frame_has_needs(model):
    frame = model.create_human_frame()
    assert isinstance(frame.needs, list)
    assert len(frame.needs) > 0


def test_human_frame_has_instincts(model):
    frame = model.create_human_frame()
    assert isinstance(frame.instincts, list)
    assert len(frame.instincts) > 0


def test_individual_frame_default_certainty(model):
    frame = model.create_individual_frame("أحمد")
    assert 0.0 <= frame.certainty <= 1.0


def test_individual_frame_evidence_list(model):
    frame = model.create_individual_frame("سارة", evidence=["ملاحظة مباشرة"])
    assert "ملاحظة مباشرة" in frame.evidence
