"""Tests for SpeechActResolver."""
from __future__ import annotations

import pytest
from mcd.mabni.speech_act_resolver import SpeechActResolver


@pytest.fixture
def resolver():
    return SpeechActResolver()


def test_question_not_assertion(resolver):
    result = resolver.resolve("هل جاء زيد؟")
    assert result.speech_act == "istifham"
    assert result.is_assertion is False
    assert result.establishes_reality is False


def test_khabar_is_assertion(resolver):
    result = resolver.resolve("جاء زيد")
    assert result.speech_act == "khabar"
    assert result.is_assertion is True


def test_nahy(resolver):
    result = resolver.resolve("لا تكذب")
    assert result.speech_act == "nahy"
    assert result.is_assertion is False


def test_tamanni_not_reality(resolver):
    result = resolver.resolve("ليت زيداً هنا")
    assert result.establishes_reality is False


def test_question_not_reality(resolver):
    result = resolver.resolve("هل جاء؟")
    assert result.establishes_reality is False
    assert result.is_assertion is False


def test_to_dict(resolver):
    result = resolver.resolve("هل جاء؟")
    d = result.to_dict()
    assert "speech_act" in d
    assert "is_assertion" in d
    assert "establishes_reality" in d
    assert d["is_assertion"] is False
