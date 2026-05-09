"""Tests for ArabicNormalizer."""
from __future__ import annotations

import pytest
from mcd.engines.normalizer import ArabicNormalizer, NormalizationMode


@pytest.fixture
def normalizer():
    return ArabicNormalizer()


def test_strict_removes_diacritics(normalizer):
    result = normalizer.normalize("مُحَمَّد", NormalizationMode.STRICT)
    assert '\u064e' not in result  # fatha
    assert '\u064f' not in result  # damma
    assert 'م' in result


def test_strict_removes_tatweel(normalizer):
    result = normalizer.normalize("الـكِتَابَةُ", NormalizationMode.STRICT)
    assert '\u0640' not in result


def test_strict_normalizes_alef(normalizer):
    result = normalizer.normalize("آدم", NormalizationMode.STRICT)
    assert 'آ' not in result
    assert result.startswith('ا')


def test_light_keeps_diacritics(normalizer):
    text = "مُحَمَّد"
    result = normalizer.normalize(text, NormalizationMode.LIGHT)
    # Light mode does NOT remove diacritics
    assert 'م' in result


def test_light_removes_tatweel(normalizer):
    result = normalizer.normalize("الـكتاب", NormalizationMode.LIGHT)
    assert '\u0640' not in result


def test_light_normalizes_alef(normalizer):
    result = normalizer.normalize("أحمد", NormalizationMode.LIGHT)
    assert 'أ' not in result
    assert result.startswith('ا')


def test_search_removes_diacritics(normalizer):
    result = normalizer.normalize("كِتَابٌ", NormalizationMode.SEARCH)
    assert '\u064e' not in result
    assert '\u064c' not in result


def test_search_normalizes_alef(normalizer):
    result = normalizer.normalize("إنسان", NormalizationMode.SEARCH)
    assert result.startswith('ا')


def test_whitespace_normalized(normalizer):
    result = normalizer.normalize("النار   تحرق", NormalizationMode.LIGHT)
    assert '  ' not in result
    assert result == "النار تحرق"


def test_yeh_normalization(normalizer):
    result = normalizer.normalize("يحيى", NormalizationMode.LIGHT)
    assert 'ى' not in result
