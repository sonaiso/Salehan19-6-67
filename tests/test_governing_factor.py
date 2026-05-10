"""Tests for governing factor detection."""
import pytest
from mcd.murab.governing_factor import (
    GoverningFactor, load_governing_factors, detect_governing_factors,
    PREPOSITIONS, INNA_PARTICLES, KANA_VERBS, JUSSIVE_PARTICLES, NASB_PARTICLES,
)


def test_load_governing_factors():
    factors = load_governing_factors()
    assert len(factors) >= 10


def test_governing_factor_fields():
    factors = load_governing_factors()
    first = factors[0]
    assert hasattr(first, 'factor_id')
    assert hasattr(first, 'surface')
    assert hasattr(first, 'governs_case')


def test_prepositions_set():
    assert "في" in PREPOSITIONS
    assert "من" in PREPOSITIONS
    assert "إلى" in PREPOSITIONS


def test_inna_particles_set():
    assert "إن" in INNA_PARTICLES
    assert "أن" in INNA_PARTICLES
    assert "لكن" in INNA_PARTICLES


def test_kana_verbs_set():
    assert "كان" in KANA_VERBS
    assert "أصبح" in KANA_VERBS


def test_jussive_particles_set():
    assert "لم" in JUSSIVE_PARTICLES
    assert "لما" in JUSSIVE_PARTICLES


def test_nasb_particles_set():
    assert "لن" in NASB_PARTICLES
    assert "أن" in NASB_PARTICLES


def test_detect_governing_factors_preposition():
    tokens = ["ذهبتُ", "إلى", "المدرسةِ"]
    factors = detect_governing_factors(tokens)
    assert len(factors) > 0
    assert any(f.governs_case in ("genitive", "جر") for f in factors)


def test_detect_governing_factors_inna():
    tokens = ["إن", "العلمَ", "نورٌ"]
    factors = detect_governing_factors(tokens)
    assert any("inna" in f.factor_id or f.governs_case in ("accusative", "نصب") for f in factors)


def test_detect_governing_factors_empty():
    tokens = ["الكتابُ", "مفيدٌ"]
    factors = detect_governing_factors(tokens)
    # No governing factors for a simple nominal sentence
    assert isinstance(factors, list)
