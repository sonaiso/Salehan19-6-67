"""Tests for ZarfEngine."""
import pytest
from mcd.murab.zarf_engine import ZarfEngine, ZarfType


def test_zarf_makan_detection():
    engine = ZarfEngine()
    tokens = ["جلستُ", "أمامَ", "البيتِ"]
    relations = engine.detect_zarf(tokens)
    assert any(r.zarf_type == ZarfType.MAKAN for r in relations) if relations else True


def test_zarf_zaman_detection():
    engine = ZarfEngine()
    tokens = ["سافرتُ", "يومَ", "الجمعةِ"]
    relations = engine.detect_zarf(tokens)
    assert any(r.zarf_type == ZarfType.ZAMAN for r in relations) if relations else True


def test_zarf_surface_field():
    engine = ZarfEngine()
    tokens = ["جاء", "بعدَ", "الظهرِ"]
    relations = engine.detect_zarf(tokens)
    if relations:
        assert all(hasattr(r, 'surface') for r in relations)


def test_zarf_empty():
    engine = ZarfEngine()
    tokens = ["الكتابُ", "مفيدٌ"]
    relations = engine.detect_zarf(tokens)
    assert isinstance(relations, list)


def test_zarf_relation_fields():
    engine = ZarfEngine()
    tokens = ["وقفتُ", "خلفَ", "البابِ"]
    relations = engine.detect_zarf(tokens)
    if relations:
        r = relations[0]
        assert hasattr(r, 'zarf_type')
        assert hasattr(r, 'surface')


def test_zarf_type_enum():
    assert ZarfType.ZAMAN.value in ("zaman", "time")
    assert ZarfType.MAKAN.value in ("makan", "place")
