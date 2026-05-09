"""Tests for LexicalGroundingEngine."""
import pytest
from mcd.grounding.lexical_grounding import LexicalGroundingEngine
from mcd.grounding.grounded_frame import GroundingStatus
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data


@pytest.fixture
def engine():
    store = PriorKnowledgeStore()
    load_seed_data(store)
    return LexicalGroundingEngine(store)


def test_fire_grounded(engine):
    result = engine.ground("نار")
    assert result.grounding_status in (GroundingStatus.GROUNDED, GroundingStatus.PARTIALLY_GROUNDED)
    assert result.certainty > 0.0


def test_ilm_without_context_partially_grounded(engine):
    result = engine.ground("علم")
    assert result.grounding_status == GroundingStatus.PARTIALLY_GROUNDED
    assert "requires_context" in result.notes or result.certainty < 0.8


def test_haram_without_shari_evidence_partially_grounded(engine):
    result = engine.ground("حرام")
    assert result.grounding_status == GroundingStatus.PARTIALLY_GROUNDED
    assert result.certainty < 0.6


def test_unknown_word_ungrounded(engine):
    result = engine.ground("كلمةمجهولةجداً")
    # Very long unknown word — certainty should be very low or ungrounded
    assert result.grounding_status in (GroundingStatus.UNGROUNDED, GroundingStatus.PARTIALLY_GROUNDED)
    assert result.certainty < 0.5


def test_grounded_lexeme_has_surface(engine):
    result = engine.ground("ماء")
    assert result.surface == "ماء"
    assert result.normalized is not None


def test_grounded_lexeme_fields(engine):
    result = engine.ground("نار")
    assert result.lexeme_id
    assert result.dal == "نار"
