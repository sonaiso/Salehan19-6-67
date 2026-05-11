"""Tests for JussiveResolver."""
import pytest
from mcd.murab.jussive_resolver import JussiveResolver


def test_lam_jussive():
    """jazim governing factor makes verb jussive."""
    resolver = JussiveResolver()
    result = resolver.resolve("يذهبْ", "jazim")
    assert "syntactic_role" in result


def test_lamma_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("يصلْ", "jazim")
    assert isinstance(result, dict)


def test_la_nahy_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("تكذبْ", "jazim")
    assert "syntactic_role" in result


def test_conditional_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("تجتهدْ", "jazim")
    assert "syntactic_role" in result


def test_jussive_marker():
    resolver = JussiveResolver()
    result = resolver.resolve("يكتبْ", "jazim")
    assert isinstance(result, dict)
