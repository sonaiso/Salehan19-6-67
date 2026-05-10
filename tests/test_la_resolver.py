"""Tests for LaResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.la_resolver import LaResolver


@pytest.fixture
def resolver():
    return LaResolver()


def test_nahy(resolver):
    result = resolver.resolve("لا تكذب")
    assert result.resolved_type in ("nahy", "nahiya")
    assert result.operator.creates_evidence is False


def test_nafy_jins(resolver):
    result = resolver.resolve("لا رجلَ في الدار")
    assert result.resolved_type in ("nafy_jins", "nafy", "negation")
    assert result.operator.creates_evidence is False


def test_creates_evidence_always_false(resolver):
    for text in ["لا تكذب", "لا رجلَ", "لا أعلم"]:
        result = resolver.resolve(text)
        assert result.operator.creates_evidence is False


def test_to_dict(resolver):
    result = resolver.resolve("لا تكذب")
    d = result.to_dict()
    assert "resolved_type" in d
    assert d["operator"]["creates_evidence"] is False
