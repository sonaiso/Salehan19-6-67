"""Tests for PrepositionResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.preposition_resolver import PrepositionResolver


@pytest.fixture
def resolver():
    return PrepositionResolver()


def test_locative_fi(resolver):
    result = resolver.resolve("في", "الكتاب في المكتبة")
    assert result.certainty_effect == "none"
    assert result.surface == "في"


def test_certainty_always_none(resolver):
    for prep in ["في", "من", "إلى", "على", "عن", "ب", "ل", "ك"]:
        result = resolver.resolve(prep)
        assert result.certainty_effect == "none", f"certainty_effect must be 'none' for '{prep}'"


def test_to_dict(resolver):
    result = resolver.resolve("في")
    d = result.to_dict()
    assert "surface" in d
    assert "certainty_effect" in d
    assert d["certainty_effect"] == "none"


def test_resolve_all(resolver):
    results = resolver.resolve_all("ذهب إلى البيت في المساء")
    assert isinstance(results, list)
    for r in results:
        assert r.certainty_effect == "none"
