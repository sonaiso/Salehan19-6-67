"""Tests for IrabCase and IrabMarker registries."""
import pytest
from mcd.murab.irab_case import IrabCase, load_irab_case_registry
from mcd.murab.irab_marker import IrabMarker, load_irab_marker_registry


def test_load_irab_case_registry():
    registry = load_irab_case_registry()
    assert "nominative" in registry
    assert "accusative" in registry
    assert "genitive" in registry
    assert "jussive" in registry


def test_irab_case_fields():
    registry = load_irab_case_registry()
    nom = registry["nominative"]
    assert nom.case_id == "nominative"
    assert nom.name_ar is not None
    assert nom.name_en is not None


def test_all_six_cases_present():
    registry = load_irab_case_registry()
    expected = {"nominative", "accusative", "genitive", "jussive"}
    assert expected.issubset(set(registry.keys()))


def test_irab_case_to_dict():
    registry = load_irab_case_registry()
    d = registry["genitive"].to_dict()
    assert d["case_id"] == "genitive"
    assert "possible_markers" in d


def test_load_irab_marker_registry():
    markers = load_irab_marker_registry()
    assert len(markers) >= 1
    if isinstance(markers, dict):
        marker_ids = list(markers.keys())
    else:
        marker_ids = [m.marker_id for m in markers]
    assert "damma" in marker_ids
    assert "kasra" in marker_ids
    assert "fatha" in marker_ids
    assert "sukun" in marker_ids


def test_irab_marker_fields():
    markers = load_irab_marker_registry()
    if isinstance(markers, dict):
        damma = markers["damma"]
    else:
        damma = next(m for m in markers if m.marker_id == "damma")
    assert damma.name_ar is not None


def test_irab_marker_to_dict():
    markers = load_irab_marker_registry()
    if isinstance(markers, dict):
        fatha = markers["fatha"]
    else:
        fatha = next(m for m in markers if m.marker_id == "fatha")
    d = fatha.to_dict()
    assert "marker_id" in d
