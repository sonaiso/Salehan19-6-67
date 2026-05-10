"""Tests for JussiveResolver."""
import pytest
from mcd.murab.jussive_resolver import JussiveResolver


def test_lam_jussive():
    """لم makes imperfect verb jussive."""
    resolver = JussiveResolver()
    result = resolver.resolve("يذهبْ", ["لم", "يذهبْ"], 1)
    assert result["syntactic_role"] == "jussive_verb"
    assert result["governing"] == "لم"


def test_lamma_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("يصلْ", ["لما", "يصلْ"], 1)
    assert result["governing"] == "لما"
    assert result["jussive_type"] == "negation_still"


def test_la_nahy_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("تكذبْ", ["لا", "تكذبْ"], 1)
    assert result["governing"] == "لا"
    assert result["jussive_type"] == "prohibition"


def test_conditional_jussive():
    resolver = JussiveResolver()
    result = resolver.resolve("تجتهدْ", ["إن", "تجتهدْ", "تنجحْ"], 1)
    assert result["syntactic_role"] == "jussive_verb"


def test_jussive_marker():
    resolver = JussiveResolver()
    result = resolver.resolve("يكتبْ", ["لم", "يكتبْ"], 1)
    assert isinstance(result, dict)
    assert result["governing"] == "لم"
