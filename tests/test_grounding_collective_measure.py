"""Tests for CollectiveMeasureModel."""
import pytest
from mcd.grounding.collective_measure import CollectiveMeasureModel, CollectiveMeasureFrame


@pytest.fixture
def model():
    return CollectiveMeasureModel()


def test_hurriya_low_certainty(model):
    frame = model.analyze("الحرية مقياس المجتمع")
    assert isinstance(frame, CollectiveMeasureFrame)
    assert frame.certainty < 0.5


def test_freedom_warns_which_freedom(model):
    frame = model.analyze("الحرية مقياس المجتمع")
    assert "which_freedom_not_specified" in frame.warnings


def test_freedom_warns_civilizational_concept(model):
    frame = model.analyze("الحرية مقياس المجتمع")
    assert "freedom_is_civilizational_concept" in frame.warnings


def test_no_evidence_warns(model):
    frame = model.analyze("الحرية مقياس المجتمع")
    assert "no_evidence_for_collective_measure" in frame.warnings


def test_slogan_warning(model):
    frame = model.analyze("الحرية مقياس المجتمع")
    assert "may_be_slogan_not_real_measure" in frame.warnings


def test_with_system_support_higher_institutional(model):
    frame = model.analyze("الحرية مكفولة بموجب القانون")
    assert frame.institutional_support > 0.0


def test_frame_fields(model):
    frame = model.analyze("العدالة مقياس أساسي")
    assert frame.measure
    assert isinstance(frame.behavioral_effects, list)
    assert isinstance(frame.evidence, list)
