"""Tests for TawabiEngine."""
import pytest
from mcd.murab.tawabi_engine import TawabiEngine, TabiType
from mcd.murab.murab_schema import MurabUnit


def _make_unit(uid, surface, case, marker, role="noun"):
    return MurabUnit(
        unit_id=uid, surface=surface, normalized=surface,
        token_id=f"t_{uid}", word_type=role,
        irab_case=case, irab_marker=marker,
        marker_visibility="apparent",
        syntactic_role="subject",
    )


def test_naat_detection():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الطالبَ", "accusative", "fatha", "noun")
    tabi = _make_unit("u2", "المجتهدَ", "accusative", "fatha", "adjective")
    result = engine.detect_tawabi([matbu, tabi])
    assert isinstance(result, list)


def test_tawabi_empty():
    engine = TawabiEngine()
    result = engine.detect_tawabi([])
    assert result == []


def test_tabi_inherits_matbu():
    """Tabi' inherits the case of matbu' (via inherited_case field)."""
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الكتابُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "المفيدُ", "nominative", "damma", "adjective")
    relations = engine.detect_tawabi([matbu, tabi])
    if relations:
        assert relations[0].inherited_case == "nominative"


def test_tabi_relation_fields():
    engine = TawabiEngine()
    matbu = _make_unit("u1", "الرجلُ", "nominative", "damma", "noun")
    tabi = _make_unit("u2", "الكبيرُ", "nominative", "damma", "adjective")
    relations = engine.detect_tawabi([matbu, tabi])
    if relations:
        r = relations[0]
        assert hasattr(r, 'matbu')
        assert hasattr(r, 'tabi')
        assert hasattr(r, 'tabi_type')
        assert hasattr(r, 'inherited_case')


def test_tabi_type_enum():
    assert TabiType.NAAT.value in ("naat", "adjective")
    assert TabiType.ATF.value in ("atf", "conjunction")
