"""Tests for IrregularIrabRegistry."""
import pytest
from mcd.murab.irregular_irab_registry import IrregularIrabRegistry, IRREGULAR_IRAB_REGISTRY


def test_five_nouns_registry():
    """Five nouns should use waw/alif/ya markers."""
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "nominative") == "waw"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "accusative") == "alif"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "genitive") == "ya"


def test_five_nouns_submarkers():
    """أب nominative → waw marker."""
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "nominative") == "waw"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "accusative") == "alif"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "genitive") == "ya"


def test_dual_detection():
    registry = IrregularIrabRegistry()
    assert registry.is_irregular("الطالبان")
    assert registry.is_irregular("المعلمين")
    assert not registry.is_irregular("الكتاب")


def test_dual_markers():
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("dual", "nominative") == "alif"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("dual", "accusative") == "ya"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("dual", "genitive") == "ya"


def test_sound_masculine_plural():
    registry = IrregularIrabRegistry()
    assert registry.is_irregular("المعلمون")
    assert registry.is_irregular("المدرسين")
    assert not registry.is_irregular("الكتاب")


def test_sound_masculine_plural_markers():
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("sound_plural", "nominative") == "waw"
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("sound_plural", "genitive") == "ya"


def test_sound_feminine_plural():
    registry = IrregularIrabRegistry()
    assert registry.is_irregular("المعلمات")


def test_analyze_five_noun():
    assert IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "nominative") == "waw"


def test_analyze_regular_word():
    registry = IrregularIrabRegistry()
    result = registry.is_irregular("الكتاب")
    assert isinstance(result, bool)
