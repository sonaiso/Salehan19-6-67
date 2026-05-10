"""Tests for EmphasisEvidenceSeparator."""
from __future__ import annotations

import pytest
from mcd.mabni.emphasis_evidence_separator import EmphasisEvidenceSeparator


@pytest.fixture
def separator():
    return EmphasisEvidenceSeparator()


def test_inna_emphasis_no_evidence(separator):
    result = separator.analyze("إنّ زيداً قائم")
    assert result.has_emphasis is True
    assert result.creates_evidence is False
    assert result.certainty_increase == 0.0


def test_qad_emphasis_no_evidence(separator):
    result = separator.analyze("قد جاء زيد")
    assert result.has_emphasis is True
    assert result.creates_evidence is False
    assert result.certainty_increase == 0.0


def test_creates_evidence_always_false(separator):
    for text in ["إنّ زيداً", "قد جاء", "والله لأفعلن", "لقد علمتَ"]:
        result = separator.analyze(text)
        assert result.creates_evidence is False


def test_certainty_increase_always_zero(separator):
    for text in ["إنّ زيداً", "قد جاء", "إنما الحق"]:
        result = separator.analyze(text)
        assert result.certainty_increase == 0.0


def test_warning_issued(separator):
    result = separator.analyze("إنّ زيداً قائم")
    assert len(result.warnings) > 0
    assert any("emphasis" in w.lower() for w in result.warnings)


def test_to_dict(separator):
    result = separator.analyze("قد جاء")
    d = result.to_dict()
    assert "creates_evidence" in d
    assert d["creates_evidence"] is False
    assert "certainty_increase" in d
    assert d["certainty_increase"] == 0.0
