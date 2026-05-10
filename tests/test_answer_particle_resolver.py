"""Tests for AnswerParticleResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.answer_particle_resolver import AnswerParticleResolver


@pytest.fixture
def resolver():
    return AnswerParticleResolver()


def test_na_am_affirmative(resolver):
    result = resolver.resolve("نعم", previous_question="هل جاء؟")
    assert result.answer_type == "affirmative"
    assert result.reverses_negation is False


def test_bala_reverses_negation(resolver):
    result = resolver.resolve("بلى", previous_question="ألم يجئ؟")
    assert result.reverses_negation is True
    assert result.answer_type == "reversal_affirmative"


def test_no_context_warning(resolver):
    result = resolver.resolve("نعم")
    assert any("context" in w.lower() for w in result.warnings)


def test_la_negative(resolver):
    result = resolver.resolve("لا", previous_question="هل جاء؟")
    assert result.answer_type == "negative"


def test_kalla_strong_negative(resolver):
    result = resolver.resolve("كلا", previous_question="هل فعلت؟")
    assert result.answer_type == "strong_negative"


def test_to_dict(resolver):
    result = resolver.resolve("نعم", previous_question="هل جاء؟")
    d = result.to_dict()
    assert "answer_type" in d
    assert "reverses_negation" in d
