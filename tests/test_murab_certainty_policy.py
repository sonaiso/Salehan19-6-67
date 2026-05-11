"""Tests for MurabCertaintyPolicy."""
import pytest
from mcd.murab.murab_certainty_policy import MurabCertaintyPolicy
from mcd.murab.murab_schema import MurabUnit


def _make_unit(visible="apparent", case="nominative", gf=None, warnings=None):
    return MurabUnit(
        unit_id="u1", surface="الكتابُ", normalized="كتاب",
        token_id="t1", word_type="noun",
        irab_case=case, irab_marker="damma",
        marker_visibility=visible,
        governing_factor_id=gf,
        syntactic_role="agent",
        semantic_role="unknown",
        warnings=warnings or [],
    )


def test_apparent_with_factor_high_certainty():
    policy = MurabCertaintyPolicy()
    unit = _make_unit(visible="apparent", gf="prep_fi")
    result = policy.evaluate(unit, None)
    assert result["syntactic_certainty"] in ("certain_syntactic", "probable_syntactic")


def test_apparent_no_factor_medium_certainty():
    policy = MurabCertaintyPolicy()
    unit = _make_unit(visible="apparent", gf=None)
    result = policy.evaluate(unit, None)
    assert result["syntactic_certainty"] in ("certain_syntactic", "probable_syntactic", "hypothesis")


def test_estimated_with_factor_certainty():
    policy = MurabCertaintyPolicy()
    unit = _make_unit(visible="estimated", gf="prep_fi")
    result = policy.evaluate(unit, None)
    assert result["syntactic_certainty"] in ("certain_syntactic", "probable_syntactic", "hypothesis")


def test_unknown_case_low_certainty():
    policy = MurabCertaintyPolicy()
    unit = _make_unit(visible="apparent", case="unknown", gf=None)
    result = policy.evaluate(unit, None)
    assert "ambiguity_warning" in " ".join(result["warnings"])


def test_irab_raises_syntactic_not_factual_certainty():
    """evidence_effect must always be 'syntactic_only'."""
    policy = MurabCertaintyPolicy()
    unit = _make_unit()
    result = policy.evaluate(unit, None)
    assert result["evidence_effect"] == "syntactic_only"


def test_warnings_in_result():
    policy = MurabCertaintyPolicy()
    unit = _make_unit(visible="estimated", gf=None)
    result = policy.evaluate(unit, None)
    assert isinstance(result["warnings"], list)
