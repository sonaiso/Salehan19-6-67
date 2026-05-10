"""Tests for MabniTraceLinker."""
from __future__ import annotations

import pytest
from mcd.mabni.mabni_trace_linker import MabniTraceLinker


@pytest.fixture
def linker():
    return MabniTraceLinker()


def test_basic_trace(linker):
    text = "ما جاء زيد"
    unfold_result = {"ma_result": {"operator_id": "MA_NEG", "surface": "ما", "creates_evidence": False}}
    report = linker.link(text, unfold_result)
    assert len(report.links) == len(text.split())


def test_links_have_required_fields(linker):
    text = "إن جاء فأكرمه"
    report = linker.link(text, {})
    for lnk in report.links:
        d = lnk.to_dict()
        assert "unicode_token" in d
        assert "token_idx" in d
        assert "operator_id" in d
        assert "judgment_status" in d


def test_to_dict(linker):
    text = "ما"
    report = linker.link(text, {})
    d = report.to_dict()
    assert "links" in d
    assert isinstance(d["links"], list)
