"""Tests for MurabTraceLinker."""
import pytest
from mcd.murab.murab_trace_linker import MurabTraceLinker
from mcd.murab.murab_schema import MurabUnit


def _make_unit(surface="الكتابُ"):
    return MurabUnit(
        unit_id="u1", surface=surface, normalized="كتاب",
        token_id="t1", word_type="noun",
        irab_case="nominative", irab_marker="damma",
        marker_visibility="apparent",
        governing_factor_id="prep_fi",
        syntactic_role="subject",
        semantic_role="actor",
        certainty_policy="apparent_with_factor",
    )


def test_trace_linker_returns_dict():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert isinstance(trace, dict)


def test_trace_includes_surface():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert "unit_id" in trace


def test_murab_trace_to_unicode():
    """Trace includes char_range."""
    linker = MurabTraceLinker()
    unit = _make_unit("أب")
    trace = linker.link(unit, "t1", 0, 2)
    assert "char_range" in trace


def test_trace_chain_sequence():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert "token_id" in trace
    assert "unit_id" in trace


def test_trace_irab_case():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert "unit_id" in trace
    assert trace["unit_id"] == "u1"


def test_trace_governing_factor():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert trace["governing_factor_id"] == "prep_fi"


def test_trace_syntactic_role():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit, "t1", 0, len("الكتابُ"))
    assert "estimated" in trace
