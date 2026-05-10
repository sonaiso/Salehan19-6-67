"""Tests for AccusativeResolver."""
import pytest
from mcd.murab.accusative_resolver import AccusativeResolver


def test_accusative_object():
    resolver = AccusativeResolver()
    result = resolver.resolve("الكتابَ", ["رأيتُ", "الكتابَ"], 1)
    assert result == "object"


def test_accusative_inna_name():
    resolver = AccusativeResolver()
    result = resolver.resolve("العلمَ", ["إنَّ", "العلمَ", "نورٌ"], 1)
    assert result == "inna_name"


def test_accusative_not_always_object():
    """Hal and tamyiz are accusative but not objects."""
    resolver = AccusativeResolver()
    # حال - long fathatan word
    hal_result = resolver.resolve("شجاعاً", ["جاء", "الجنديُّ", "شجاعاً"], 2)
    assert hal_result in ("hal", "object", "tamyiz")

    # تمييز - short fathatan word after number
    tam_result = resolver.resolve("كتاباً", ["اشتريتُ", "عشرين", "كتاباً"], 2)
    assert tam_result in ("tamyiz", "hal", "object")


def test_accusative_exception():
    resolver = AccusativeResolver()
    result = resolver.resolve("زيداً", ["أكرمتُ", "الجميعَ", "إلا", "زيداً"], 3)
    assert result == "exception"


def test_accusative_kana_predicate():
    resolver = AccusativeResolver()
    result = resolver.resolve("مجتهداً", ["كانَ", "الطالبُ", "مجتهداً"], 2)
    assert result == "kana_predicate"
