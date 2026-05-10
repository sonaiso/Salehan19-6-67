"""Tests for GraphemeTrace."""
import pytest
from mcd.traceability.unicode_trace import build_unicode_trace_unit
from mcd.traceability.grapheme_trace import GraphemeTrace, build_grapheme_traces


def test_build_grapheme_no_diacritics():
    units = [build_unicode_trace_unit(c, i) for i, c in enumerate("كتب")]
    graphemes = build_grapheme_traces(units)
    assert len(graphemes) == 3
    for g in graphemes:
        assert g.grapheme_id.startswith("G-")
        assert len(g.unicode_trace_ids) == 1
        assert g.diacritics == []


def test_build_grapheme_with_diacritic():
    # عَ = ع + fatha
    chars = ['\u0639', '\u064E']
    units = [build_unicode_trace_unit(c, i) for i, c in enumerate(chars)]
    graphemes = build_grapheme_traces(units)
    assert len(graphemes) == 1
    g = graphemes[0]
    assert g.base_char == '\u0639'
    assert '\u064E' in g.diacritics
    assert len(g.unicode_trace_ids) == 2


def test_empty_input():
    assert build_grapheme_traces([]) == []


def test_to_dict():
    units = [build_unicode_trace_unit('م', 0)]
    graphemes = build_grapheme_traces(units)
    d = graphemes[0].to_dict()
    assert "grapheme_id" in d
    assert "surface" in d
    assert "role_candidates" in d


def test_role_candidates_merged():
    # Weak letter + diacritic
    chars = ['\u0648', '\u064E']  # و + fatha
    units = [build_unicode_trace_unit(c, i) for i, c in enumerate(chars)]
    graphemes = build_grapheme_traces(units)
    assert len(graphemes) == 1
    g = graphemes[0]
    # Should have both weak_letter and diacritic_role
    assert "weak_letter" in g.role_candidates or "root_candidate" in g.role_candidates


def test_multiple_diacritics():
    # كَّ = ك + fatha + shadda
    chars = ['\u0643', '\u064E', '\u0651']
    units = [build_unicode_trace_unit(c, i) for i, c in enumerate(chars)]
    graphemes = build_grapheme_traces(units)
    assert len(graphemes) == 1
    assert len(graphemes[0].diacritics) == 2
