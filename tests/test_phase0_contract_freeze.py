from __future__ import annotations

from mcd.core.public_judgment import enforce_governed_output_contract
from mcd.fractal_kernel import KernelValidator
from mcd.fractal_kernel import ProofObject as FKProofObject
from mcd.fractal_kernel import ReverseTrace as FKReverseTrace
from mcd.math_governance import TransitionInput, phi_transition
from mcd.cfk.reverse_trace import ReverseTrace as CFKReverseTrace


def _phi_payload(condition):
    return TransitionInput(
        U="0*",
        P="token[0]",
        L="left_context",
        R="right_context",
        G="token_to_lexeme",
        C=condition,
        W=["witness-1"],
        X={"context": "sample"},
    )


def test_phase0_phi_tri_state_contract_locked():
    suspended = phi_transition(_phi_payload(None))
    blocked = phi_transition(_phi_payload(False))
    allowed = phi_transition(_phi_payload(True))

    assert (suspended.judgment, suspended.known, suspended.passed) == ("suspended", 0, 0)
    assert "transition_condition_unknown" in suspended.residuals

    assert (blocked.judgment, blocked.known, blocked.passed) == ("blocked", 1, 0)
    assert "transition_condition_failed" in blocked.residuals

    assert (allowed.judgment, allowed.known, allowed.passed) == ("allowed", 1, 1)
    assert allowed.residuals == []


def test_phase0_certificate_requires_raw_text_anchor():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-raw",
            "judgment": "certificate",
            "governance_gate_passed": True,
            "reverse_trace_obj": {"reverse_trace_id": "RT-raw", "complete": False, "raw_text_units": []},
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "certificate_without_reverse_trace" in payload["residuals"]


def test_phase0_no_certificate_with_blocking_residuals():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-res",
            "judgment": "certificate",
            "governance_gate_passed": True,
            "reverse_trace_ref": "RT-res",
            "residuals": ["blocking_residual"],
        }
    )
    assert payload["judgment"] == "hypothesis"


def test_phase0_no_silent_level_skip_certificate():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-silent",
            "judgment": "certificate",
            "governance_gate_passed": True,
            "reverse_trace_ref": "RT-silent",
            "transition_tags": ["silent_level_skip"],
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "silent_level_skip" in payload["residuals"]


def test_phase0_certificate_rejected_without_reverse_trace():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-no-rt",
            "judgment": "certificate",
            "governance_gate_passed": True,
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "certificate_without_reverse_trace" in payload["residuals"]


def test_phase0_certificate_rejected_without_proof_object():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "",
            "judgment": "certificate",
            "governance_gate_passed": True,
            "reverse_trace_ref": "RT-no-proof",
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "certificate_without_proof_object" in payload["residuals"]


def test_phase0_certificate_rejected_without_governance_gate():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-no-gate",
            "judgment": "certificate",
            "governance_gate_passed": False,
            "reverse_trace_ref": "RT-no-gate",
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "certificate_without_governance_gate" in payload["residuals"]


def test_phase0_reverse_trace_serialization_preserves_raw_text_units():
    cfk_trace = CFKReverseTrace(
        reverse_trace_id="RT-cfk",
        final_judgment="hypothesis",
        proof_id="PO-cfk",
        raw_text_units=["النار حارة"],
        complete=True,
    )
    cfk_roundtrip = CFKReverseTrace(**cfk_trace.to_dict())
    assert cfk_roundtrip.raw_text_units == ["النار حارة"]

    fk_trace = FKReverseTrace(
        reverse_trace_id="RT-fk",
        final_claim="النار حارة",
        proof_id="PO-fk",
        raw_text_units=["النار حارة"],
        complete=True,
    )
    fk_roundtrip = FKReverseTrace(**fk_trace.to_dict())
    assert fk_roundtrip.raw_text_units == ["النار حارة"]


def test_phase0_reverse_trace_completeness_requires_raw_text_units_in_cfk_and_fractal_kernel_paths():
    validator = KernelValidator()
    proof = FKProofObject(
        proof_id="P1",
        claim_id="C1",
        proof_status="certificate",
        evidence_refs=["E1"],
        reverse_trace_id="RT-1",
    )
    reverse_trace = FKReverseTrace(
        reverse_trace_id="RT-1",
        final_claim="النار حارة",
        proof_id="P1",
        complete=True,
        raw_text_units=[],
    )
    ok, violations = validator.validate_proof_object(proof, {"RT-1": reverse_trace})
    assert ok is False
    assert any("missing raw_text_units" in v for v in violations)
