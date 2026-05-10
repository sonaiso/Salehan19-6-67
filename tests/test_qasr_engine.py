"""Tests for QasrEngine."""
from __future__ import annotations

import pytest
from mcd.mabni.qasr_engine import QasrEngine


@pytest.fixture
def engine():
    return QasrEngine()


def test_innama_qasr(engine):
    result = engine.analyze("إنما الأعمال بالنيات")
    assert result.qasr_type == "innama_qasr"
    assert result.particle == "إنما"
    assert result.is_evidence is False


def test_ma_illa_qasr(engine):
    result = engine.analyze("ما محمد إلا رسول")
    assert "illa" in result.qasr_type
    assert result.is_evidence is False


def test_la_illa_qasr(engine):
    result = engine.analyze("لا إله إلا الله")
    assert "illa" in result.qasr_type
    assert result.is_evidence is False


def test_is_evidence_always_false(engine):
    for text in ["إنما الحق", "ما هو إلا إنسان", "لا نجاح إلا بالجد"]:
        result = engine.analyze(text)
        assert result.is_evidence is False


def test_to_dict(engine):
    result = engine.analyze("إنما الأعمال بالنيات")
    d = result.to_dict()
    assert "qasr_type" in d
    assert "is_evidence" in d
    assert d["is_evidence"] is False
