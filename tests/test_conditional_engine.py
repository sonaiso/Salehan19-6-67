"""Tests for ConditionalEngine."""
from __future__ import annotations

import pytest
from mcd.mabni.conditional_engine import ConditionalEngine


@pytest.fixture
def engine():
    return ConditionalEngine()


def test_in_conditional(engine):
    result = engine.analyze("إن جاء زيد فأكرمه")
    assert result.condition_type in ("real_condition", "possible_condition", "conditional")
    assert result.judgment_suspended is True


def test_idha_conditional(engine):
    result = engine.analyze("إذا طلعت الشمس خرجنا")
    assert result.judgment_suspended is True


def test_law_conditional(engine):
    result = engine.analyze("لو جاء لأكرمناه")
    assert result.judgment_suspended is True


def test_lawla_conditional(engine):
    result = engine.analyze("لولا المطر لذهبنا")
    assert result.judgment_suspended is True


def test_judgment_always_suspended(engine):
    for text in ["إن جاء", "إذا طلع", "لو كان", "لولا الله"]:
        result = engine.analyze(text)
        assert result.judgment_suspended is True, f"judgment_suspended must be True for '{text}'"


def test_to_dict(engine):
    result = engine.analyze("إن جاء زيد فأكرمه")
    d = result.to_dict()
    assert "judgment_suspended" in d
    assert d["judgment_suspended"] is True
    assert "condition_type" in d
