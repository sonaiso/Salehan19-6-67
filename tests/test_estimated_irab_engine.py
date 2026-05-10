"""Tests for EstimatedIrabEngine."""
import pytest
from mcd.murab.estimated_irab_engine import EstimatedIrabEngine


def test_maqsur_estimated_damma():
    engine = EstimatedIrabEngine()
    result = engine.resolve("الفتى", "nominative")
    assert result["has_estimated_marker"] is True
    assert "maqsur" in result["reason"]


def test_manqus_estimated():
    engine = EstimatedIrabEngine()
    result = engine.resolve("القاضي", "nominative")
    assert result["has_estimated_marker"] is True
    assert result["visibility"] == "estimated"


def test_muzaf_ya_estimated():
    engine = EstimatedIrabEngine()
    result = engine.resolve("كتابي", "genitive")
    assert result["has_estimated_marker"] is True


def test_regular_word_not_estimated():
    engine = EstimatedIrabEngine()
    result = engine.resolve("الكتابُ", "nominative")
    assert result["has_estimated_marker"] is False


def test_estimated_irab_maqsur():
    """الفتى has estimated damma for nominative."""
    engine = EstimatedIrabEngine()
    result = engine.resolve("الفتى", "nominative")
    assert result["has_estimated_marker"] is True
    assert result["visibility"] == "estimated"


def test_estimated_result_fields():
    engine = EstimatedIrabEngine()
    result = engine.resolve("الهدى", "nominative")
    assert "has_estimated_marker" in result
    assert "visibility" in result
    assert "reason" in result


def test_estimated_type_values():
    engine = EstimatedIrabEngine()
    r = engine.resolve("الفتى", "nominative")
    assert r["reason"] in (
        "maqsur_last_letter_alif_or_alif_maqsura",
        "manqus_last_letter_ya",
        "mudaf_ila_ya_mutakallim",
        "no_estimated_marker",
    )
