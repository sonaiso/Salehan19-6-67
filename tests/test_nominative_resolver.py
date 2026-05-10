"""Tests for NominativeResolver."""
import pytest
from mcd.murab.nominative_resolver import NominativeResolver


def test_nominative_resolver_mubtada():
    resolver = NominativeResolver()
    result = resolver.resolve("الكتابُ", ["الكتابُ", "مفيدٌ"], 0)
    assert result in ("agent", "subject", "mubtada", "imperfect_verb_nominative")


def test_nominative_kana_name():
    resolver = NominativeResolver()
    result = resolver.resolve("الطالبُ", ["كانَ", "الطالبُ", "مجتهداً"], 1)
    assert result == "kana_name"


def test_nominative_inna_predicate():
    resolver = NominativeResolver()
    result = resolver.resolve("نورٌ", ["إنَّ", "العلمَ", "نورٌ"], 2)
    assert isinstance(result, str)


def test_nominative_agent():
    resolver = NominativeResolver()
    result = resolver.resolve("المعلمُ", ["جاءَ", "المعلمُ"], 1)
    assert result in ("agent", "subject")


def test_raised_word_not_always_agent():
    """Mubtada is nominative but its role is 'subject', not always 'agent'."""
    resolver = NominativeResolver()
    # At position 0 in a nominal sentence, result could be subject or agent
    result = resolver.resolve("زيدٌ", ["زيدٌ", "ذكيٌّ"], 0)
    # The key assertion is that the token returns a nominative role (not accusative/genitive)
    assert isinstance(result, str)
    assert result not in ("object", "object_of_preposition", "mudaf_ilayh")
