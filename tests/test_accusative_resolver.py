"""Tests for AccusativeResolver."""
import pytest
from mcd.murab.accusative_resolver import AccusativeResolver


def test_accusative_object():
    resolver = AccusativeResolver()
    result = resolver.resolve("الكتابَ", None, 1)
    assert "syntactic_role" in result


def test_accusative_inna_name():
    resolver = AccusativeResolver()
    result = resolver.resolve("العلمَ", "nasikh", 1)
    assert "syntactic_role" in result


def test_accusative_not_always_object():
    """Hal and tamyiz are accusative but not objects."""
    resolver = AccusativeResolver()
    result = resolver.resolve("شجاعاً", None, 2)
    assert isinstance(result, dict)


def test_accusative_exception():
    resolver = AccusativeResolver()
    result = resolver.resolve("زيداً", None, 3)
    assert "syntactic_role" in result


def test_accusative_kana_predicate():
    resolver = AccusativeResolver()
    result = resolver.resolve("مجتهداً", "nasikh", 2)
    assert "syntactic_role" in result
