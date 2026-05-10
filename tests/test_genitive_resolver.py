"""Tests for GenitiveResolver."""
import pytest
from mcd.murab.genitive_resolver import GenitiveResolver


def test_genitive_preposition():
    resolver = GenitiveResolver()
    result = resolver.resolve("المدرسةِ", "preposition")
    assert "syntactic_role" in result


def test_genitive_mudaf_ilayh():
    resolver = GenitiveResolver()
    result = resolver.resolve("الطالبِ", "idafa")
    assert "syntactic_role" in result


def test_genitive_idafa_not_always_ownership():
    """Idafa can express specification not just ownership."""
    resolver = GenitiveResolver()
    result = resolver.resolve("العلمِ", "idafa")
    assert isinstance(result, dict)


def test_genitive_preposition_min():
    resolver = GenitiveResolver()
    result = resolver.resolve("المغربِ", "preposition")
    assert "syntactic_role" in result


def test_genitive_to_dict():
    resolver = GenitiveResolver()
    result = resolver.resolve("البيتِ", "preposition")
    assert isinstance(result, dict)
    assert "syntactic_role" in result
