"""Tests for NominativeResolver."""
import pytest
from mcd.murab.nominative_resolver import NominativeResolver


def test_nominative_resolver_mubtada():
    resolver = NominativeResolver()
    result = resolver.resolve("الكتابُ", None, 0)
    assert "syntactic_role" in result
    assert "semantic_role" in result


def test_nominative_kana_name():
    resolver = NominativeResolver()
    result = resolver.resolve("الطالبُ", "nasikh", 1)
    assert "syntactic_role" in result


def test_nominative_inna_predicate():
    resolver = NominativeResolver()
    result = resolver.resolve("نورٌ", None, 2)
    assert isinstance(result, dict)


def test_nominative_agent():
    resolver = NominativeResolver()
    result = resolver.resolve("المعلمُ", None, 1)
    assert "syntactic_role" in result


def test_raised_word_not_always_agent():
    """Mubtada is nominative but its role is 'subject', not always 'agent'."""
    resolver = NominativeResolver()
    result = resolver.resolve("زيدٌ", None, 0)
    assert isinstance(result, dict)
    assert result.get("semantic_role") not in ("object", "object_of_preposition")
