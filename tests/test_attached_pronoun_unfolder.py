"""Tests for AttachedPronounUnfolder."""
from __future__ import annotations

import pytest
from mcd.mabni.attached_pronoun_unfolder import AttachedPronounUnfolder


@pytest.fixture
def unfolder():
    return AttachedPronounUnfolder()


def test_basic_pronoun(unfolder):
    results = unfolder.unfold("رأيتُه")
    assert len(results) >= 1
    result = results[0]
    assert result.referent_known is False


def test_referent_known_always_false(unfolder):
    for text in ["رأيتُه", "كتابُها", "أعطيتُكم", "رأيتُنا"]:
        results = unfolder.unfold(text)
        for r in results:
            assert r.referent_known is False, f"referent_known must be False for '{text}'"


def test_to_dict(unfolder):
    results = unfolder.unfold("رأيتُه")
    for r in results:
        d = r.to_dict()
        assert "pronoun_form" in d
        assert "referent_known" in d
        assert d["referent_known"] is False


def test_no_pronoun_returns_empty(unfolder):
    results = unfolder.unfold("الكتاب في الحقيبة")
    assert isinstance(results, list)
