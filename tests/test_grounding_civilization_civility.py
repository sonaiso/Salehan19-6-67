"""Tests for CivilizationCivilityDeepClassifier."""
import pytest
from mcd.grounding.civilization_civility_classifier import (
    CivilizationCivilityDeepClassifier,
    CivilizationCivilityResult,
)


@pytest.fixture
def classifier():
    return CivilizationCivilityDeepClassifier()


def test_ai_is_civility(classifier):
    result = classifier.classify("الذكاء الاصطناعي")
    assert result.is_civility is True


def test_ai_risk_of_value_transfer(classifier):
    result = classifier.classify("الذكاء الاصطناعي")
    assert result.risk_of_value_transfer > 0.0


def test_pure_tool_is_civility_not_civilization(classifier):
    result = classifier.classify("سيارة")
    assert result.is_civility is True
    assert result.is_civilization is False


def test_value_concept_is_civilization(classifier):
    result = classifier.classify("الديمقراطية")
    assert result.is_civilization is True


def test_islam_is_civilization(classifier):
    result = classifier.classify("الإسلام")
    assert result.is_civilization is True


def test_result_has_explanation(classifier):
    result = classifier.classify("الذكاء الاصطناعي")
    assert result.explanation
    assert result.item == "الذكاء الاصطناعي"


def test_certainty_positive(classifier):
    result = classifier.classify("سيارة")
    assert result.certainty > 0.0


def test_ai_with_value_context_partial_civilization(classifier):
    result = classifier.classify("الذكاء الاصطناعي", context="القرار والسلطة")
    assert result.is_civility is True
    # With value context, may also flag civilization
    assert result.risk_of_value_transfer > 0.0
