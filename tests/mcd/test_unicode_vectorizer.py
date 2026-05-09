"""Tests for UnicodeVectorizer."""
from __future__ import annotations

import pytest
from mcd.engines.unicode_vectorizer import UnicodeVectorizer


@pytest.fixture
def vectorizer():
    return UnicodeVectorizer()


def test_arabic_letter_ka(vectorizer):
    v = vectorizer.vectorize('ك')
    assert v.is_arabic is True
    assert v.is_letter is True
    assert v.is_diacritic is False
    assert v.is_space is False


def test_space(vectorizer):
    v = vectorizer.vectorize(' ')
    assert v.is_space is True
    assert v.is_letter is False
    assert v.is_arabic is False


def test_diacritic_fatha(vectorizer):
    v = vectorizer.vectorize('\u064e')
    assert v.is_diacritic is True
    assert v.diacritic_role == 'fatha'


def test_alef_connects_right_not_left(vectorizer):
    v = vectorizer.vectorize('ا')
    assert v.connects_right is True
    assert v.connects_left is False


def test_ba_connects_both(vectorizer):
    v = vectorizer.vectorize('ب')
    assert v.connects_right is True
    assert v.connects_left is True


def test_root_candidate_score_strong_consonant(vectorizer):
    v = vectorizer.vectorize('ك')
    assert v.root_candidate_score == 0.8


def test_root_candidate_score_weak_letter(vectorizer):
    v = vectorizer.vectorize('و')
    assert v.root_candidate_score == 0.3


def test_vectorize_word(vectorizer):
    vecs = vectorizer.vectorize_word('كتب')
    assert len(vecs) == 3
    assert all(v.is_arabic for v in vecs)


def test_vectorize_text_returns_pairs(vectorizer):
    pairs = vectorizer.vectorize_text('ك ب')
    assert len(pairs) == 3
    assert pairs[0][0] == 'ك'
    assert pairs[1][0] == ' '


def test_features_in_valid_range(vectorizer):
    for ch in 'كتابة':
        v = vectorizer.vectorize(ch)
        assert 0.0 <= v.root_candidate_score <= 1.0
        assert 0.0 <= v.affix_candidate_score <= 1.0
        assert 0.0 <= v.weak_letter_score <= 1.0
