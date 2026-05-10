"""Tests for ExceptionRestrictionEngine."""
from __future__ import annotations

import pytest
from mcd.mabni.exception_restriction_engine import ExceptionRestrictionEngine


@pytest.fixture
def engine():
    return ExceptionRestrictionEngine()


def test_basic_exception(engine):
    result = engine.analyze("جاء القوم إلا زيداً")
    assert result.particle == "إلا"
    assert result.scope_modified is True
    assert result.is_evidence is False


def test_ghayr(engine):
    result = engine.analyze("أكل الجميع غير زيد")
    assert result.particle == "غير"
    assert result.is_evidence is False


def test_siwa(engine):
    result = engine.analyze("جاؤوا سوى واحد")
    assert result.particle == "سوى"
    assert result.is_evidence is False


def test_is_evidence_always_false(engine):
    for text in ["جاء القوم إلا زيداً", "نجح الكل غير محمد", "ما جاء إلا عمرو"]:
        result = engine.analyze(text)
        assert result.is_evidence is False


def test_no_exception_warning(engine):
    result = engine.analyze("جاء زيد")
    assert len(result.warnings) > 0


def test_to_dict(engine):
    result = engine.analyze("جاء القوم إلا زيداً")
    d = result.to_dict()
    assert "particle" in d
    assert "is_evidence" in d
    assert d["is_evidence"] is False
