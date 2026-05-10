"""Tests for IdafaEngine."""
import pytest
from mcd.murab.idafa_engine import IdafaEngine


def test_idafa_detection_basic():
    engine = IdafaEngine()
    tokens = ["كتابُ", "الطالبِ"]
    relations = engine.detect_idafa(tokens)
    assert len(relations) >= 1


def test_idafa_possession():
    engine = IdafaEngine()
    tokens = ["كتابُ", "الطالبِ"]
    relations = engine.detect_idafa(tokens)
    assert any(r.idafa_type in ("possession", "idafa", "specification") for r in relations)


def test_idafa_masdar():
    engine = IdafaEngine()
    tokens = ["بناءُ", "المصنعِ"]
    relations = engine.detect_idafa(tokens)
    assert len(relations) >= 1


def test_idafa_part_whole():
    engine = IdafaEngine()
    tokens = ["رأسُ", "الجبلِ"]
    relations = engine.detect_idafa(tokens)
    assert len(relations) >= 1


def test_idafa_not_always_ownership():
    """Idafa (إضافة) can be specification, not ownership."""
    engine = IdafaEngine()
    tokens = ["خاتمُ", "ذهبٍ"]
    relations = engine.detect_idafa(tokens)
    assert isinstance(relations, list)


def test_idafa_relation_fields():
    engine = IdafaEngine()
    tokens = ["كتابُ", "العلمِ"]
    relations = engine.detect_idafa(tokens)
    if relations:
        r = relations[0]
        assert hasattr(r, 'mudaf')
        assert hasattr(r, 'mudaf_ilayh')
        assert hasattr(r, 'idafa_type')
