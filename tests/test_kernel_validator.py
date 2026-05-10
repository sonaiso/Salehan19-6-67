import pytest
from mcd.fractal_kernel import (
    KernelValidator, CognitiveFractalUnit, UnifiedVector,
    CognitiveOperator, ProofObject, ReverseTrace
)


def make_unit(**kwargs):
    defaults = dict(unit_id="CFU-001", level="word", unit_type="lexical",
                    fold_state="atomic", trace_refs=["T-001"])
    defaults.update(kwargs)
    return CognitiveFractalUnit(**defaults)


def test_validate_valid_unit():
    validator = KernelValidator()
    unit = make_unit()
    ok, viol = validator.validate_unit(unit)
    assert ok is True
    assert len(viol) == 0


def test_validate_unit_no_trace_no_generated():
    validator = KernelValidator()
    unit = make_unit(trace_refs=[])
    ok, viol = validator.validate_unit(unit)
    assert ok is False


def test_validate_valid_vector():
    validator = KernelValidator()
    v = UnifiedVector(vector_id="V1", vector_type="role",
                      dimensions={"role_vector": 0.5}, source_unit_ids=["CFU-001"])
    ok, viol = validator.validate_vector(v)
    assert ok is True


def test_validate_invalid_vector_unknown_dim():
    validator = KernelValidator()
    v = UnifiedVector(vector_id="V1", vector_type="role",
                      dimensions={"bad_dim": 0.5}, source_unit_ids=["CFU-001"])
    ok, viol = validator.validate_vector(v)
    assert ok is False


def test_validate_operator_no_evidence_creation():
    validator = KernelValidator()
    op = CognitiveOperator("op1", "morphological", creates_evidence=False)
    ok, viol = validator.validate_operator(op)
    assert ok is True


def test_validate_proof_requires_reverse_trace():
    validator = KernelValidator()
    proof = ProofObject(proof_id="P1", claim_id="C1", proof_status="hypothesis")
    ok, viol = validator.validate_proof_object(proof, {})
    assert ok is False


def test_full_validation_empty():
    validator = KernelValidator()
    report = validator.run_full_validation()
    assert report.passed is True
    assert report.kernel_validation_score >= 0.98


def test_full_validation_with_valid_units():
    validator = KernelValidator()
    units = [make_unit(unit_id=f"CFU-{i}", trace_refs=["T-001"]) for i in range(5)]
    report = validator.run_full_validation(units=units)
    assert report.unit_validity_score == 1.0
