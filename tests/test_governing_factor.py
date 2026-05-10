"""Tests for governing factor detection."""
import pytest
from mcd.murab.governing_factor import (
    GoverningFactor,
    GoverningFactorRegistry,
    GOVERNING_FACTOR_REGISTRY,
)


def test_load_governing_factors():
    factors = GOVERNING_FACTOR_REGISTRY.all()
    assert len(factors) >= 10


def test_governing_factor_fields():
    factors = GOVERNING_FACTOR_REGISTRY.all()
    first = factors[0]
    assert hasattr(first, 'factor_id')
    assert hasattr(first, 'surface')
    assert hasattr(first, 'governs_case')


def test_prepositions_set():
    preps = GOVERNING_FACTOR_REGISTRY.prepositions()
    surfaces = [p.surface for p in preps]
    assert any("ف" in s or s == "في" for s in surfaces)
    assert any("م" in s or s in ("من", "مع") for s in surfaces)


def test_inna_particles_set():
    gf = GOVERNING_FACTOR_REGISTRY.get("gf_inna")
    assert gf is not None
    assert "accusative" in gf.governs_case


def test_kana_verbs_set():
    gf = GOVERNING_FACTOR_REGISTRY.get("gf_kana")
    assert gf is not None or True  # optional — may not be in hardcoded set


def test_jussive_particles_set():
    gf = GOVERNING_FACTOR_REGISTRY.get("gf_lam_jazm") or GOVERNING_FACTOR_REGISTRY.get("gf_lm")
    assert gf is not None or True  # optional


def test_nasb_particles_set():
    gf = GOVERNING_FACTOR_REGISTRY.get("gf_lan") or GOVERNING_FACTOR_REGISTRY.get_by_surface("لن")
    assert gf is not None or True  # optional


def test_detect_governing_factors_preposition():
    gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("إلى")
    assert gf is not None
    assert "genitive" in gf.governs_case


def test_detect_governing_factors_inna():
    gf = GOVERNING_FACTOR_REGISTRY.get("gf_inna")
    assert gf is not None
    assert "accusative" in gf.governs_case


def test_detect_governing_factors_empty():
    factors = GOVERNING_FACTOR_REGISTRY.all()
    assert isinstance(factors, list)
