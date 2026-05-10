"""Tests for UnicodeTraceUnit."""
import pytest
from mcd.traceability.unicode_trace import (
    UnicodeTraceUnit, TRACE_STATUSES,
    build_unicode_trace_unit, _classify_char,
)


def test_build_arabic_letter():
    unit = build_unicode_trace_unit('ك', 0)
    assert unit.trace_id.startswith("U-")
    assert unit.char == 'ك'
    assert unit.is_arabic is True
    assert unit.is_letter is True
    assert unit.is_diacritic is False
    assert unit.trace_status == "classified"
    assert unit.char_index == 0


def test_build_diacritic():
    unit = build_unicode_trace_unit('\u064E', 1)  # fatha
    assert unit.is_diacritic is True
    assert unit.is_arabic is True
    assert unit.trace_status == "classified"
    assert "diacritic_role" in unit.role_candidates


def test_build_space():
    unit = build_unicode_trace_unit(' ', 2)
    assert unit.is_space is True
    assert unit.trace_status == "ignored_for_semantics_but_tracked"


def test_build_unknown_char():
    unit = build_unicode_trace_unit('\x00', 0)
    assert unit.trace_id != ""
    assert unit.trace_status in TRACE_STATUSES


def test_all_statuses_valid():
    for s in TRACE_STATUSES:
        assert isinstance(s, str)


def test_trace_id_unique():
    u1 = build_unicode_trace_unit('ا', 0)
    u2 = build_unicode_trace_unit('ا', 0)
    assert u1.trace_id != u2.trace_id


def test_to_dict_keys():
    unit = build_unicode_trace_unit('ب', 3)
    d = unit.to_dict()
    required = [
        "trace_id", "char", "unicode_code", "char_index",
        "unicode_name", "unicode_category", "bidi_class",
        "normalized_nfc", "normalized_nfd",
        "is_arabic", "is_letter", "is_diacritic", "is_space", "is_punctuation",
        "feature_vector", "role_candidates", "trace_status",
    ]
    for k in required:
        assert k in d, f"Missing key: {k}"


def test_invalid_status_raises():
    with pytest.raises(ValueError):
        UnicodeTraceUnit(
            trace_id="X", char="a", unicode_code=97, char_index=0,
            unicode_name="LATIN SMALL LETTER A", unicode_category="Ll",
            bidi_class="L", normalized_nfc="a", normalized_nfd="a",
            is_arabic=False, is_letter=True, is_diacritic=False,
            is_space=False, is_punctuation=False,
            feature_vector={}, role_candidates={},
            trace_status="bad_status",
        )


def test_latin_char():
    unit = build_unicode_trace_unit('A', 5)
    assert unit.trace_status == "classified"
    assert unit.is_arabic is False


def test_punctuation_char():
    unit = build_unicode_trace_unit('.', 0)
    assert unit.is_punctuation is True
    assert unit.trace_status == "ignored_for_semantics_but_tracked"


def test_number_char():
    unit = build_unicode_trace_unit('5', 0)
    assert unit.trace_status == "classified"
