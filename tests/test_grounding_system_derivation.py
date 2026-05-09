"""Tests for SystemDerivationModel."""
import pytest
from mcd.grounding.system_derivation import SystemDerivationModel, SystemDerivation


@pytest.fixture
def model():
    return SystemDerivationModel()


def test_system_keyword_detected(model):
    text = "نريد نظامًا تعليميًا"
    result = model.derive(text)
    assert result is not None
    assert isinstance(result, SystemDerivation)
    assert result.system_name


def test_no_system_keyword_returns_none(model):
    text = "الجو جميل اليوم"
    result = model.derive(text)
    assert result is None


def test_system_name_contains_text(model):
    text = "نريد نظامًا تعليميًا"
    result = model.derive(text)
    assert result is not None
    assert len(result.system_name) > 0


def test_default_certainty_low(model):
    text = "نريد نظامًا تعليميًا"
    result = model.derive(text)
    assert result is not None
    assert result.certainty < 0.8


def test_manzouma_keyword(model):
    text = "نحتاج إلى منظومة تعليمية متكاملة"
    result = model.derive(text)
    assert result is not None


def test_result_fields(model):
    text = "هذا النظام يحل المشكلة"
    result = model.derive(text)
    assert result is not None
    assert isinstance(result.rules, list)
    assert isinstance(result.procedures, list)
    assert isinstance(result.institutions, list)
