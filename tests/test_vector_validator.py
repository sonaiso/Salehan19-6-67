"""Tests for VectorValidator."""
from mcd.curriculum.vector_validator import VectorValidationResult, validate_role_vector, validate_domain_vector
from mcd.curriculum.role_vector import build_role_vector
from mcd.curriculum.domain_vector import build_domain_vector

def test_validate_role_vector_valid():
    v = build_role_vector("thing")
    r = validate_role_vector(v)
    assert isinstance(r, VectorValidationResult)

def test_validate_domain_vector_valid():
    v = build_domain_vector(["economics"])
    r = validate_domain_vector(v)
    assert isinstance(r, VectorValidationResult)

def test_result_to_dict():
    r = validate_role_vector(build_role_vector("thing"))
    d = r.to_dict()
    assert "passed" in d and "score" in d

def test_score_between_0_and_1():
    r = validate_role_vector(build_role_vector("agent"))
    assert 0.0 <= r.score <= 1.0

def test_empty_vector_has_violations():
    r = validate_role_vector({})
    assert len(r.violations) > 0
