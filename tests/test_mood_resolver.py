"""Tests for MoodResolver (imperfect verb moods)."""
import pytest
from mcd.murab.mood_resolver import MoodResolver


def test_jussive_mood():
    resolver = MoodResolver()
    result = resolver.resolve("يذهبْ", ["لم", "يذهبْ"], 1)
    assert result == "jussive"


def test_lan_accusative_mood():
    """لن makes imperfect verb accusative_mood (منصوب) not jussive."""
    resolver = MoodResolver()
    result = resolver.resolve("يذهبَ", ["لن", "يذهبَ"], 1)
    assert result == "accusative_mood"


def test_nominative_mood_default():
    resolver = MoodResolver()
    result = resolver.resolve("يكتبُ", ["هو", "يكتبُ"], 1)
    assert result == "nominative_mood"


def test_an_accusative_mood():
    resolver = MoodResolver()
    result = resolver.resolve("يدرسَ", ["أريدُ", "أن", "يدرسَ"], 2)
    assert result == "accusative_mood"


def test_mood_marker_preserved():
    resolver = MoodResolver()
    result = resolver.resolve("يكتبُ", ["هو", "يكتبُ"], 1)
    assert isinstance(result, str)
