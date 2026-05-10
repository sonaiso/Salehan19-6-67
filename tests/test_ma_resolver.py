"""Tests for MaResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.ma_resolver import MaResolver


@pytest.fixture
def resolver():
    return MaResolver()


def test_negation_ma(resolver):
    result = resolver.resolve("ما جاء زيد")
    assert result.resolved_type == "negation"
    assert result.operator.creates_evidence is False


def test_interrogative_ma(resolver):
    result = resolver.resolve("ما هذا؟")
    assert result.resolved_type == "interrogative"
    assert result.operator.creates_evidence is False


def test_innama_qasr(resolver):
    result = resolver.resolve("إنما الأعمال بالنيات")
    assert result.resolved_type == "innama_qasr"
    assert result.operator.creates_evidence is False


def test_creates_evidence_always_false(resolver):
    for text in ["ما جاء", "ما هذا", "إنما النجاح", "ما تفعل أفعل"]:
        result = resolver.resolve(text)
        assert result.operator.creates_evidence is False, f"creates_evidence must be False for '{text}'"


def test_to_dict(resolver):
    result = resolver.resolve("ما جاء زيد")
    d = result.to_dict()
    assert "resolved_type" in d
    assert d["operator"]["creates_evidence"] is False
