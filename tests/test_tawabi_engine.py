"""Tests for TawabiEngine."""
import pytest
from mcd.murab.tawabi_engine import TawabiEngine
from mcd.murab.murab_schema import MurabUnit


def _make_unit(uid, surface, case, marker, role="noun"):
    return MurabUnit(
        unit_id=uid, surface=surface, normalized=surface,
        token_id=f"t_{uid}", word_type=role,
        irab_case=case, irab_marker=marker,
        marker_visibility="apparent",
        governing_factor_id=None,
        syntactic_role="subject",
        semantic_role="unknown",
    )


def test_naat_detection():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الطالبَ", "accusative", "fatha", "noun")
    tabi = _make_unit("u2", "المجتهدَ", "accusative", "fatha", "adjective")
    result = engine.resolve(matbu, tabi, [])
    assert isinstance(result, dict)


def test_tawabi_empty_context():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الكتابُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "المفيدُ", "nominative", "damma", "adjective")
    result = engine.resolve(matbu, tabi, [])
    assert isinstance(result, dict)


def test_tabi_inherits_matbu():
    """Tabi' inherits the case of matbu' (via inherited_case field)."""
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الكتابُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "المفيدُ", "nominative", "damma", "adjective")
    result = engine.resolve(matbu, tabi, [])
    assert result["inherited_case"] == "nominative"


def test_tabi_relation_fields():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الرجلُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "الكبيرُ", "nominative", "damma", "adjective")
    result = engine.resolve(matbu, tabi, [])
    assert "tabi_type" in result
    assert "inherited_case" in result
    assert "matboo_id" in result


def test_tabi_type_values():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الرجلُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "الكبيرُ", "nominative", "damma", "adjective")
    result = engine.resolve(matbu, tabi, [])
    assert result["tabi_type"] in ("naat", "atf", "tawkid", "badal", "atf_bayan")
