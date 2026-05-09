"""Tests for vector_space module."""
from mcd.curriculum.vector_space import (
    ROLE_DIMENSIONS, zero_role_vector, zero_domain_vector,
    normalize_vector, validate_vector_dimensions,
)

def test_role_dimensions_nonempty(): assert len(ROLE_DIMENSIONS) > 0
def test_zero_role_vector_has_all_dims():
    v = zero_role_vector()
    assert all(d in v for d in ROLE_DIMENSIONS)
def test_zero_role_vector_all_zero(): assert all(x == 0.0 for x in zero_role_vector().values())
def test_zero_domain_vector_nonempty(): assert isinstance(zero_domain_vector(), dict)
def test_normalize_vector_sums_to_one():
    v = {"a": 1.0, "b": 3.0}
    n = normalize_vector(v)
    assert abs(sum(n.values()) - 1.0) < 1e-9
def test_normalize_empty_vector():
    assert normalize_vector({}) == {}
def test_validate_vector_no_violations():
    v = {d: 0.0 for d in ROLE_DIMENSIONS}
    assert validate_vector_dimensions(v, ROLE_DIMENSIONS) == []
def test_validate_vector_extra_dim():
    v = {d: 0.0 for d in ROLE_DIMENSIONS}
    v["UNKNOWN_DIM"] = 1.0
    violations = validate_vector_dimensions(v, ROLE_DIMENSIONS)
    assert any("UNKNOWN_DIM" in vi for vi in violations)
