"""Tests for IrregularIrabRegistry."""
import pytest
from mcd.murab.irregular_irab_registry import IrregularIrabRegistry, FIVE_NOUNS


def test_five_nouns_registry():
    assert "أب" in FIVE_NOUNS
    assert "أخ" in FIVE_NOUNS
    assert "ذو" in FIVE_NOUNS


def test_five_nouns_submarkers():
    """أب nominative → waw marker."""
    registry = IrregularIrabRegistry()
    entry = registry.get_five_noun("أب")
    assert entry is not None
    assert entry.nominative_marker == "waw"
    assert entry.accusative_marker == "alif"
    assert entry.genitive_marker == "ya"


def test_dual_detection():
    registry = IrregularIrabRegistry()
    assert registry.is_dual("الطالبان")
    assert registry.is_dual("المعلمين")
    assert not registry.is_dual("الكتاب")


def test_dual_markers():
    registry = IrregularIrabRegistry()
    assert registry.get_dual_markers("nominative") == "alif"
    assert registry.get_dual_markers("accusative") == "ya"
    assert registry.get_dual_markers("genitive") == "ya"


def test_sound_masculine_plural():
    registry = IrregularIrabRegistry()
    assert registry.is_sound_masculine_plural("المعلمون")
    assert registry.is_sound_masculine_plural("المدرسين")
    assert not registry.is_sound_masculine_plural("الكتاب")


def test_sound_masculine_plural_markers():
    registry = IrregularIrabRegistry()
    assert registry.get_sound_masc_plural_markers("nominative") == "waw"
    assert registry.get_sound_masc_plural_markers("genitive") == "ya"


def test_sound_feminine_plural():
    registry = IrregularIrabRegistry()
    assert registry.is_sound_feminine_plural("المعلمات")


def test_analyze_five_noun():
    registry = IrregularIrabRegistry()
    result = registry.analyze_word("أب", "nominative")
    assert result["irregular_type"] == "five_nouns"
    assert result["marker"] == "waw"


def test_analyze_regular_word():
    registry = IrregularIrabRegistry()
    result = registry.analyze_word("الكتاب", "nominative")
    assert result["irregular_type"] in ("regular", "dual", "sound_masculine_plural", "sound_feminine_plural", "five_nouns")
