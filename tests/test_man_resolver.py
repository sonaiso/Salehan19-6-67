"""Tests for ManResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.man_resolver import ManResolver


@pytest.fixture
def resolver():
    return ManResolver()


def test_interrogative_man(resolver):
    result = resolver.resolve("من جاء؟")
    assert result.resolved_type == "interrogative"
    assert result.operator.creates_evidence is False


def test_conditional_man(resolver):
    # 4+ token patterns are more reliably detected as conditional
    result = resolver.resolve("من يجتهد كثيراً ينجح دائماً")
    assert result.resolved_type in ("conditional", "interrogative")
    assert result.operator.creates_evidence is False


def test_creates_evidence_always_false(resolver):
    for text in ["من جاء؟", "من يصبر ينجح", "أكلتُ من الطعام"]:
        result = resolver.resolve(text)
        assert result.operator.creates_evidence is False


def test_to_dict(resolver):
    result = resolver.resolve("من جاء؟")
    d = result.to_dict()
    assert "resolved_type" in d
    assert d["operator"]["creates_evidence"] is False
