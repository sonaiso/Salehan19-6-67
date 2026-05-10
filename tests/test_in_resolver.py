"""Tests for InResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.in_resolver import InResolver


@pytest.fixture
def resolver():
    return InResolver()


def test_conditional_in(resolver):
    result = resolver.resolve("إن جاء زيد فأكرمه")
    assert result.resolved_type == "in_conditional"
    assert result.operator.creates_evidence is False


def test_inna_emphasis(resolver):
    result = resolver.resolve("إنّ زيداً قائم")
    assert result.resolved_type == "inna_emphasis"
    assert result.operator.creates_evidence is False


def test_innama_qasr(resolver):
    result = resolver.resolve("إنما الأعمال بالنيات")
    assert result.resolved_type == "innama_qasr"
    assert result.operator.creates_evidence is False


def test_creates_evidence_always_false(resolver):
    for text in ["إن جاء", "إنّ زيداً", "إنما الحق"]:
        result = resolver.resolve(text)
        assert result.operator.creates_evidence is False


def test_to_dict(resolver):
    result = resolver.resolve("إن تفعل تنجح")
    d = result.to_dict()
    assert "resolved_type" in d
    assert d["operator"]["creates_evidence"] is False
