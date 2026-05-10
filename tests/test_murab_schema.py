"""Tests for MurabUnit schema."""
import pytest
from mcd.murab.murab_schema import MurabUnit


def test_murab_unit_creation():
    unit = MurabUnit(
        unit_id="u1",
        surface="الكتابُ",
        normalized="كتاب",
        token_id="t1",
        word_type="noun",
        irab_case="nominative",
        irab_marker="damma",
        marker_visibility="apparent",
    )
    assert unit.irab_case == "nominative"
    assert unit.irab_marker == "damma"


def test_murab_unit_defaults():
    unit = MurabUnit(
        unit_id="u2",
        surface="الولدُ",
        normalized="ولد",
        token_id="t2",
        word_type="noun",
        irab_case="nominative",
        irab_marker="damma",
        marker_visibility="apparent",
    )
    assert unit.governing_factor_id is None
    assert unit.warnings == []
    assert unit.relation_edges == []


def test_murab_unit_to_dict():
    unit = MurabUnit(
        unit_id="u3",
        surface="كتابٌ",
        normalized="كتاب",
        token_id="t3",
        word_type="noun",
        irab_case="nominative",
        irab_marker="dammatan",
        marker_visibility="apparent",
    )
    d = unit.to_dict()
    assert d["irab_case"] == "nominative"
    assert d["surface"] == "كتابٌ"


def test_murab_unit_from_dict():
    data = {
        "unit_id": "u4",
        "surface": "طالبٌ",
        "normalized": "طالب",
        "token_id": "t4",
        "word_type": "noun",
        "irab_case": "nominative",
        "irab_marker": "dammatan",
        "marker_visibility": "apparent",
        "governing_factor_id": None,
        "syntactic_role": "subject",
        "semantic_role": "actor",
        "relation_edges": [],
        "certainty_policy": "apparent_no_factor",
        "warnings": [],
        "trace_ids": [],
    }
    unit = MurabUnit.from_dict(data)
    assert unit.surface == "طالبٌ"
    assert unit.irab_case == "nominative"


def test_murab_unit_roundtrip():
    unit = MurabUnit(
        unit_id="u5",
        surface="المدرسةِ",
        normalized="مدرسة",
        token_id="t5",
        word_type="noun",
        irab_case="genitive",
        irab_marker="kasra",
        marker_visibility="apparent",
        governing_factor_id="prep_fi",
        syntactic_role="object_of_preposition",
        semantic_role="location",
        warnings=["test"],
    )
    d = unit.to_dict()
    restored = MurabUnit.from_dict(d)
    assert restored.irab_case == unit.irab_case
    assert restored.warnings == unit.warnings
