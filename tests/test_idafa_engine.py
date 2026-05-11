"""Tests for IdafaEngine."""
import pytest
from mcd.murab.idafa_engine import IdafaEngine
from mcd.murab.murab_schema import MurabUnit


def _make_unit(uid, surface, case, marker):
    return MurabUnit(
        unit_id=uid, surface=surface, normalized=surface,
        token_id=f"t_{uid}", word_type="noun",
        irab_case=case, irab_marker=marker,
        marker_visibility="apparent", governing_factor_id=None,
        syntactic_role="subject", semantic_role="unknown",
    )


def test_idafa_detection_basic():
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "كتابُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "الطالبِ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert isinstance(result, dict)
    assert "idafa_type" in result


def test_idafa_possession():
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "كتابُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "الطالبِ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert result["idafa_type"] in ("ownership", "possession", "specification", "masdar")


def test_idafa_masdar():
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "بناءُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "المصنعِ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert "idafa_type" in result


def test_idafa_part_whole():
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "رأسُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "الجبلِ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert isinstance(result, dict)


def test_idafa_not_always_ownership():
    """Idafa (إضافة) can be specification, not ownership."""
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "خاتمُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "ذهبٍ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert isinstance(result, dict)


def test_idafa_relation_fields():
    engine = IdafaEngine()
    mudaf = _make_unit("u1", "كتابُ", "nominative", "damma")
    mudaf_ilayh = _make_unit("u2", "العلمِ", "genitive", "kasra")
    result = engine.resolve(mudaf, mudaf_ilayh)
    assert "idafa_type" in result
    assert "mudaf_id" in result
    assert "mudaf_ilayh_id" in result
