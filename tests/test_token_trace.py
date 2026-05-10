"""Tests for TokenTrace."""
import pytest
from mcd.traceability.token_trace import TokenTrace, TOKEN_TYPES, build_token_traces, _detect_token_type
from mcd.traceability.unicode_trace import build_unicode_trace_unit
from mcd.traceability.grapheme_trace import build_grapheme_traces


def _build(text):
    units = [build_unicode_trace_unit(c, i) for i, c in enumerate(text)]
    graphemes = build_grapheme_traces(units)
    tokens = build_token_traces(text, units, graphemes)
    return units, graphemes, tokens


def test_token_types_valid():
    for t in TOKEN_TYPES:
        assert isinstance(t, str)


def test_single_word():
    _, _, tokens = _build("كتب")
    word_tokens = [t for t in tokens if t.token_type == "word"]
    assert len(word_tokens) >= 1
    for t in word_tokens:
        assert len(t.unicode_trace_ids) > 0


def test_whitespace_split():
    _, _, tokens = _build("كتب زيد")
    types = [t.token_type for t in tokens]
    assert "whitespace" in types
    assert "word" in types


def test_unicode_ids_present():
    _, _, tokens = _build("مرحبا")
    for t in tokens:
        assert len(t.unicode_trace_ids) > 0


def test_to_dict():
    _, _, tokens = _build("كتب")
    for t in tokens:
        d = t.to_dict()
        assert "token_id" in d
        assert "surface" in d
        assert "unicode_trace_ids" in d
        assert "token_type" in d


def test_invalid_token_type():
    with pytest.raises(ValueError):
        TokenTrace(
            token_id="X", surface="x", unicode_trace_ids=[],
            grapheme_ids=[], token_type="invalid",
            normalized="x", role_vector={}, domain_hint_vector={}, metadata={},
        )


def test_detect_whitespace():
    assert _detect_token_type("   ") == "whitespace"


def test_detect_number():
    assert _detect_token_type("123") == "number"
    assert _detect_token_type("٠١٢") == "number"


def test_detect_word():
    assert _detect_token_type("كتب") == "word"


def test_empty_text():
    units, graphemes, tokens = _build("")
    assert tokens == []


def test_token_grapheme_ids():
    _, graphemes, tokens = _build("كتب")
    for t in tokens:
        if t.token_type == "word":
            assert len(t.grapheme_ids) > 0
