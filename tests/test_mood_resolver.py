"""Tests for MoodResolver (imperfect verb moods)."""
import pytest
from mcd.murab.mood_resolver import MoodResolver


def test_jussive_mood():
    resolver = MoodResolver()
    result = resolver.resolve_mood("يذهبْ", "jazim")
    assert result == "jussive"


def test_lan_accusative_mood():
    """nasib makes imperfect verb subjunctive."""
    resolver = MoodResolver()
    result = resolver.resolve_mood("يذهبَ", "nasib")
    assert result == "subjunctive"


def test_nominative_mood_default():
    resolver = MoodResolver()
    result = resolver.resolve_mood("يكتبُ", None)
    assert result == "indicative"


def test_an_accusative_mood():
    resolver = MoodResolver()
    result = resolver.resolve_mood("يدرسَ", "nasib")
    assert result == "subjunctive"


def test_mood_marker_preserved():
    resolver = MoodResolver()
    result = resolver.resolve_mood("يكتبُ", None)
    assert isinstance(result, str)
