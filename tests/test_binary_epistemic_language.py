"""Tests for BEL governed binary representation."""
from __future__ import annotations

import pytest

from mcd.curriculum.binary_epistemic_language import BinaryEpistemicUnit


def _base_unit() -> BinaryEpistemicUnit:
    return BinaryEpistemicUnit(
        unit="knowledge is light",
        existence_bit=1,
        trace_bit=1,
        distinction_bit=1,
        designation_bit=1,
        identity_bit=1,
        domain_bit=1,
        relation_bit=1,
        evidence_bit=1,
        proof_object_bit=1,
        governance_gate_bit=1,
        reverse_trace_bit=1,
    )


def test_binary_epistemic_unit_exposes_architecture_contract_fields():
    unit = _base_unit()
    d = unit.to_dict()
    for key in (
        "pre", "current", "post", "phi_in", "phi_out", "beta",
        "type", "order", "composition", "invariants", "forbidden",
        "residual", "judgment",
    ):
        assert key in d
    assert isinstance(d["pre"], list)
    assert isinstance(d["post"], list)
    assert isinstance(d["composition"], list)
    assert isinstance(d["invariants"], list)
    assert isinstance(d["forbidden"], list)
    assert isinstance(d["residual"], list)
    assert d["type"] == "belief_unit"
    assert d["judgment"] == "HYPOTHESIS"
    assert unit.evaluate_judgment() == "CERTIFICATE"


def test_bit_validation_rejects_non_binary_value():
    with pytest.raises(ValueError, match="must be 0 or 1"):
        BinaryEpistemicUnit(unit="x", existence_bit=2)


def test_missing_foundational_bits_forces_zero():
    unit = _base_unit()
    unit.designation_bit = 0
    assert unit.evaluate_judgment() == "ZERO"


def test_no_certificate_without_governance_gate():
    unit = _base_unit()
    unit.governance_gate_bit = 0
    unit.forbidden = ["certificate_without_governance_gate"]
    assert unit.blocked_forbidden_transitions() == ["certificate_without_governance_gate"]
    assert unit.evaluate_judgment() == "HYPOTHESIS"


def test_certificate_requires_proofobject_governance_and_reverse_trace():
    unit = _base_unit()
    assert unit.evaluate_judgment() == "CERTIFICATE"


def test_residual_blocks_certificate_and_is_preserved():
    unit = _base_unit()
    unit.residual = ["missing_context"]
    assert unit.evaluate_judgment() == "HYPOTHESIS"
    assert unit.to_dict()["residual"] == ["missing_context"]


def test_blocked_forbidden_transitions_returns_known_entries_only():
    unit = _base_unit()
    unit.forbidden = ["certificate_without_governance_gate", "unknown_transition"]
    assert unit.blocked_forbidden_transitions() == ["certificate_without_governance_gate"]
