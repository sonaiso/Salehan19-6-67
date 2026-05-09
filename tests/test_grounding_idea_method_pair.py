"""Tests for IdeaMethodPairModel."""
import pytest
from mcd.grounding.idea_method_pair import IdeaMethodPairModel, IdeaMethodPair


@pytest.fixture
def model():
    return IdeaMethodPairModel()


def test_idea_method_extracted(model):
    text = "نريد نظامًا تعليميًا لتربية العقل"
    result = model.extract(text)
    assert result is not None
    assert isinstance(result, IdeaMethodPair)
    assert result.idea
    assert result.method


def test_no_idea_method_returns_none(model):
    text = "الجو جميل اليوم"
    result = model.extract(text)
    assert result is None


def test_idea_contains_system_keyword(model):
    text = "نريد نظامًا تعليميًا لتربية العقل"
    result = model.extract(text)
    assert result is not None
    # idea phrase should contain a system/education keyword
    assert any(kw in result.idea for kw in ["نظام", "تعليم", "تربية"])


def test_certainty_default(model):
    text = "نريد نظامًا تعليميًا لتربية العقل"
    result = model.extract(text)
    assert result is not None
    assert 0.0 <= result.certainty <= 1.0


def test_idea_method_with_minhaj(model):
    text = "الفكرة التعليمية تحتاج منهجًا واضحًا"
    result = model.extract(text)
    # "فكرة" is idea keyword, "منهج" is method keyword
    assert result is not None
