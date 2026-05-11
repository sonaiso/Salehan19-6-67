"""Tests for ZarfEngine."""
import pytest
from mcd.murab.zarf_engine import ZarfEngine


def test_zarf_makan_detection():
    engine = ZarfEngine()
    result = engine.resolve("أمام", ["جلستُ", "أمامَ", "البيتِ"])
    assert result["zarf_type"] == "makan"


def test_zarf_zaman_detection():
    engine = ZarfEngine()
    result = engine.resolve("يوم", ["سافرتُ", "يومَ", "الجمعةِ"])
    assert result["zarf_type"] == "zaman"


def test_zarf_surface_field():
    engine = ZarfEngine()
    result = engine.resolve("بعد", ["جاء", "بعدَ", "الظهرِ"])
    assert "zarf_type" in result


def test_zarf_empty():
    engine = ZarfEngine()
    result = engine.resolve("الكتاب", [])
    assert isinstance(result, dict)
    assert "zarf_type" in result


def test_zarf_relation_fields():
    engine = ZarfEngine()
    result = engine.resolve("خلف", ["وقفتُ", "خلفَ", "البابِ"])
    assert "zarf_type" in result
    assert "relation_type" in result


def test_zarf_type_values():
    engine = ZarfEngine()
    r1 = engine.resolve("يوم", [])
    assert r1["zarf_type"] == "zaman"
    r2 = engine.resolve("أمام", [])
    assert r2["zarf_type"] == "makan"
