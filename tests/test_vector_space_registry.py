import pytest
from mcd.fractal_kernel import UnifiedVector, UnifiedVectorSpaceRegistry, VectorDimension


def make_vector(**kwargs):
    defaults = dict(vector_id="VEC-001", vector_type="role",
                    dimensions={"role_vector": 0.5}, source_unit_ids=["CFU-001"])
    defaults.update(kwargs)
    return UnifiedVector(**defaults)


def test_vector_requires_source_trace_or_unit():
    with pytest.raises(ValueError):
        UnifiedVector(vector_id="V", vector_type="role",
                      dimensions={}, source_unit_ids=[], source_trace_refs=[])


def test_vector_value_out_of_range():
    with pytest.raises(ValueError):
        make_vector(dimensions={"role_vector": 1.5})


def test_valid_vector():
    v = make_vector()
    assert v.vector_id == "VEC-001"


def test_registry_knows_default_dimensions():
    reg = UnifiedVectorSpaceRegistry()
    assert "role_vector" in reg.known_dimensions()
    assert "evidence_creation" in reg.known_dimensions()
    assert "factual_certainty" in reg.known_dimensions()


def test_validate_known_dimension():
    reg = UnifiedVectorSpaceRegistry()
    v = make_vector(dimensions={"role_vector": 0.5})
    valid, violations = reg.validate_vector(v)
    assert valid is True


def test_validate_unknown_dimension():
    reg = UnifiedVectorSpaceRegistry()
    v = make_vector(dimensions={"unknown_dim_xyz": 0.5})
    valid, violations = reg.validate_vector(v)
    assert valid is False


def test_evidence_creation_mabni_blocked():
    reg = UnifiedVectorSpaceRegistry()
    v = UnifiedVector(vector_id="V", vector_type="evidence",
                      dimensions={"evidence_creation": 0.5}, source_unit_ids=["CFU-001"])
    valid, viol = reg.validate_evidence_creation(v, "mabni")
    assert valid is False
    assert len(viol) > 0


def test_factual_certainty_irab_blocked():
    reg = UnifiedVectorSpaceRegistry()
    v = UnifiedVector(vector_id="V", vector_type="certainty",
                      dimensions={"factual_certainty": 0.5}, source_unit_ids=["CFU-001"])
    valid, viol = reg.validate_factual_certainty(v, "murab")
    assert valid is False


def test_vector_to_dict():
    v = make_vector()
    d = v.to_dict()
    assert d["vector_id"] == "VEC-001"
