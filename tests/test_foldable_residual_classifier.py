"""Tests for ResidualClassifier."""
import pytest
from mcd.foldable_learning.residual_classifier import ResidualClassifier
from mcd.residual_learning.residual_schema import CognitiveResidual


def _make_residual(types, severity="medium"):
    return CognitiveResidual(residual_id="r1", proposal_id="p1", residual_types=types, severity=severity)


def test_blocking_types_classified_as_blocking():
    clf = ResidualClassifier()
    for rt in ["harm_haram_residual", "injection_residual", "gpt_as_evidence_residual"]:
        r = _make_residual([rt])
        assert clf.classify_severity(r) == "blocking"


def test_high_types_classified_as_high():
    clf = ResidualClassifier()
    r = _make_residual(["tool_evidence_residual"])
    assert clf.classify_severity(r) == "high"


def test_medium_types_classified_as_medium():
    clf = ResidualClassifier()
    r = _make_residual(["metaphor_residual"])
    assert clf.classify_severity(r) == "medium"


def test_no_types_classified_as_low():
    clf = ResidualClassifier()
    r = _make_residual([])
    assert clf.classify_severity(r) == "low"


def test_is_blocking():
    clf = ResidualClassifier()
    r = _make_residual(["gpt_as_evidence_residual"])
    assert clf.is_blocking(r)


def test_get_primary_type():
    clf = ResidualClassifier()
    r = _make_residual(["evidence_residual", "harm_haram_residual"])
    assert clf.get_primary_type(r) == "harm_haram_residual"
