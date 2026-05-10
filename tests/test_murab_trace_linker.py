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
        syntactic_role="subject",
        semantic_role="actor",
        governing_factor_id="prep_fi",
        certainty_policy="apparent_with_factor",
    )


def test_trace_linker_returns_dict():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert isinstance(trace, dict)


def test_trace_includes_surface():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert trace["surface"] == "الكتابُ"


def test_murab_trace_to_unicode():
    """Trace includes U+XXXX codepoints."""
    linker = MurabTraceLinker()
    unit = _make_unit("أب")
    trace = linker.link(unit)
    assert "unicode_trace" in trace
    for cp in trace["unicode_trace"]:
        assert cp.startswith("U+")


def test_trace_chain_sequence():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert "trace_chain" in trace
    assert len(trace["trace_chain"]) >= 5


def test_trace_irab_case():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert trace["irab_case"] == "nominative"


def test_trace_governing_factor():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert trace["governing_factor"] == "prep_fi"


def test_trace_syntactic_role():
    linker = MurabTraceLinker()
    unit = _make_unit()
    trace = linker.link(unit)
    assert trace["syntactic_role"] == "subject"
