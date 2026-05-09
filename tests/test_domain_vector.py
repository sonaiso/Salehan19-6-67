"""Tests for domain_vector module."""
from mcd.curriculum.domain_vector import build_domain_vector, validate_domain_vector, blend_domain_vectors

def test_build_domain_vector_returns_dict():
    v = build_domain_vector(["religion", "fiqh"])
    assert isinstance(v, dict)
def test_build_domain_vector_nonempty():
    v = build_domain_vector(["ethics"])
    assert len(v) > 0
def test_validate_domain_vector_valid():
    v = build_domain_vector(["economics"])
    errors = validate_domain_vector(v)
    assert isinstance(errors, list)
def test_blend_domain_vectors():
    v1 = build_domain_vector(["religion"])
    v2 = build_domain_vector(["law"])
    blended = blend_domain_vectors([v1, v2])
    assert isinstance(blended, dict)
def test_blend_empty_list():
    assert isinstance(blend_domain_vectors([]), dict)
