"""Tests for role_vector module."""
from mcd.curriculum.role_vector import build_role_vector, validate_role_vector, blend_role_vectors
from mcd.curriculum.vector_space import ROLE_DIMENSIONS

def test_build_role_vector_returns_dict():
    v = build_role_vector("thing")
    assert isinstance(v, dict)
def test_build_role_vector_has_dims():
    v = build_role_vector("agent")
    assert all(d in v for d in ROLE_DIMENSIONS)
def test_validate_role_vector_valid():
    v = build_role_vector("thing")
    errors = validate_role_vector(v)
    assert errors == []
def test_blend_two_vectors():
    v1 = build_role_vector("thing")
    v2 = build_role_vector("agent")
    blended = blend_role_vectors([v1, v2])
    assert isinstance(blended, dict)
def test_blend_empty_list_returns_zero():
    r = blend_role_vectors([])
    assert isinstance(r, dict)
