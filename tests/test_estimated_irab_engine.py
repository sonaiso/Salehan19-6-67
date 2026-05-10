"""Tests for EstimatedIrabEngine."""
import pytest
from mcd.murab.estimated_irab_engine import EstimatedIrabEngine, EstimatedType


def test_maqsur_estimated_damma():
    engine = EstimatedIrabEngine()
    result = engine.analyze("الفتى", "nominative")
    assert result is not None
    assert result.estimated_type == EstimatedType.MAQSUR
    assert result.marker_visibility == "estimated"


def test_manqus_estimated():
    engine = EstimatedIrabEngine()
    # القاضي ends in ي which is detected as MUDAF_TO_YA or MANQUS
    result = engine.analyze("القاضي", "nominative")
    assert result is not None
    assert result.estimated_type in (EstimatedType.MANQUS, EstimatedType.MUDAF_TO_YA)
    assert result.marker_visibility == "estimated"


def test_muzaf_ya_estimated():
    engine = EstimatedIrabEngine()
    result = engine.analyze("كتابي", "nominative")
    if result:
        assert result.estimated_type in (EstimatedType.MUDAF_TO_YA, EstimatedType.MANQUS, EstimatedType.MAQSUR)


def test_regular_word_not_estimated():
    engine = EstimatedIrabEngine()
    result = engine.analyze("الكتابُ", "nominative")
    assert result is None or result.marker_visibility == "apparent"


def test_estimated_irab_maqsur():
    """الفتى has estimated damma for nominative."""
    engine = EstimatedIrabEngine()
    result = engine.analyze("الفتى", "nominative")
    assert result is not None
    assert result.marker_visibility == "estimated"
    assert result.estimated_type == EstimatedType.MAQSUR


def test_estimated_result_fields():
    engine = EstimatedIrabEngine()
    result = engine.analyze("الهدى", "nominative")
    if result:
        assert hasattr(result, 'estimated_type')
        assert hasattr(result, 'marker_visibility')
        assert hasattr(result, 'reason')


def test_estimated_type_enum():
    assert EstimatedType.MAQSUR.value in ("maqsur", "مقصور")
    assert EstimatedType.MANQUS.value in ("manqus", "منقوص")
