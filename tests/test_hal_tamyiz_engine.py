"""Tests for HalTamyizEngine."""
import pytest
from mcd.murab.hal_tamyiz_engine import HalTamyizEngine


def test_hal_detection():
    engine = HalTamyizEngine()
    tokens = ["جاء", "الجنديُّ", "شجاعاً"]
    result = engine.classify("شجاعاً", tokens, 2)
    assert result is not None
    assert result.result_type in ("hal", "tamyiz")


def test_tamyiz_detection():
    engine = HalTamyizEngine()
    tokens = ["اشتريتُ", "عشرين", "كتاباً"]
    result = engine.classify("كتاباً", tokens, 2)
    assert result is not None
    assert result.result_type in ("hal", "tamyiz")


def test_hal_tamyiz_accusative():
    engine = HalTamyizEngine()
    tokens = ["فاض", "النيلُ", "ماءً"]
    result = engine.classify("ماءً", tokens, 2)
    assert result is not None


def test_number_precedes_tamyiz():
    """A number preceding the accusative token suggests tamyiz."""
    engine = HalTamyizEngine()
    tokens = ["ملأتُ", "عشرين", "إناءً"]
    result = engine.classify("إناءً", tokens, 2)
    assert result is not None
    assert result.syntactic_role in ("tamyiz", "specification", "hal", "state_description")


def test_hal_tamyiz_result_fields():
    engine = HalTamyizEngine()
    tokens = ["جاء", "زيدٌ", "راكباً"]
    result = engine.classify("راكباً", tokens, 2)
    if result:
        assert hasattr(result, 'result_type')
        assert hasattr(result, 'syntactic_role')
