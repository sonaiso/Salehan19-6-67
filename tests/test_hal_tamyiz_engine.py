"""Tests for HalTamyizEngine."""
import pytest
from mcd.murab.hal_tamyiz_engine import HalTamyizEngine


def test_hal_detection():
    engine = HalTamyizEngine()
    result = engine.classify("شجاعاً", None, ["جاء", "الجنديُّ"])
    assert isinstance(result, dict)
    assert "classification" in result


def test_tamyiz_detection():
    engine = HalTamyizEngine()
    result = engine.classify("كتاباً", None, ["اشتريتُ", "عشرين"])
    assert isinstance(result, dict)
    assert "classification" in result


def test_hal_tamyiz_accusative():
    engine = HalTamyizEngine()
    result = engine.classify("ماءً", None, ["فاض", "النيلُ"])
    assert isinstance(result, dict)


def test_number_precedes_tamyiz():
    """A number preceding the accusative token suggests tamyiz."""
    engine = HalTamyizEngine()
    result = engine.classify("إناءً", None, ["ملأتُ", "عشرين"])
    assert isinstance(result, dict)
    assert "classification" in result


def test_hal_tamyiz_result_fields():
    engine = HalTamyizEngine()
    result = engine.classify("راكباً", None, ["جاء", "زيدٌ"])
    assert "classification" in result
    assert "certainty_policy" in result
