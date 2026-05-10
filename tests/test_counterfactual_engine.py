"""Tests for CounterfactualEngine."""
from __future__ import annotations

import pytest
from mcd.mabni.counterfactual_engine import CounterfactualEngine


@pytest.fixture
def engine():
    return CounterfactualEngine()


def test_law_counterfactual(engine):
    result = engine.analyze("لو درستَ لنجحتَ")
    assert result.is_counterfactual is True
    assert result.certainty_policy == "conditional_only"


def test_lawla_counterfactual(engine):
    result = engine.analyze("لولا المطر لذهبنا")
    assert result.is_counterfactual is True
    assert result.certainty_policy == "conditional_only"


def test_non_counterfactual(engine):
    result = engine.analyze("جاء زيد")
    assert result.is_counterfactual is False


def test_certainty_policy_always_conditional_only(engine):
    for text in ["لو جاء", "لولا الله", "لوما المطر"]:
        result = engine.analyze(text)
        if result.is_counterfactual:
            assert result.certainty_policy == "conditional_only"


def test_to_dict(engine):
    result = engine.analyze("لو درستَ لنجحتَ")
    d = result.to_dict()
    assert "is_counterfactual" in d
    assert "certainty_policy" in d
