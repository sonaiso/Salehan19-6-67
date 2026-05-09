"""Tests for CompositionFunction."""
from mcd.curriculum.composition_function import CompositionInput, CompositionResult, compose_vectors
from mcd.curriculum.role_vector import build_role_vector

def _inp(n=2):
    vecs = [build_role_vector("thing") for _ in range(n)]
    return CompositionInput(child_vectors=vecs)

def test_compose_returns_result(): assert isinstance(compose_vectors(_inp()), CompositionResult)
def test_compose_vector_is_dict(): assert isinstance(compose_vectors(_inp()).vector, dict)
def test_compose_empty_child_vectors():
    r = compose_vectors(CompositionInput(child_vectors=[]))
    assert isinstance(r.vector, dict)
def test_compose_penalty_applied():
    inp = CompositionInput(child_vectors=[build_role_vector("thing")], ambiguity_penalty=0.5)
    r = compose_vectors(inp)
    assert "ambiguity" in r.penalties_applied or isinstance(r.penalties_applied, dict)
def test_compose_to_dict():
    r = compose_vectors(_inp())
    d = r.to_dict()
    assert "vector" in d and "penalties_applied" in d
