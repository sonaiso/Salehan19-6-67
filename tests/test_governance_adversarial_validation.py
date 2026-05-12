from __future__ import annotations

from mcd.governance.adversarial_validation import AdversarialAttempt, evaluate_adversarial_attempt


def test_fake_certificate_is_downgraded_to_hypothesis():
    attempt = AdversarialAttempt(
        attempt_id="ATT-001",
        requested_judgment="certificate",
        proof_object_ref="",
        governance_gate_passed=False,
        reverse_trace_ref="",
        evidence_matches_claim=False,
    )
    result = evaluate_adversarial_attempt(attempt)
    assert result.public_judgment == "hypothesis"
    assert "certificate_without_proof_object" in result.blocked_reasons
    assert "certificate_without_governance_gate" in result.blocked_reasons
    assert "certificate_without_reverse_trace" in result.blocked_reasons


def test_valid_certificate_is_allowed():
    attempt = AdversarialAttempt(
        attempt_id="ATT-002",
        requested_judgment="certificate",
        proof_object_ref="PO-1",
        governance_gate_passed=True,
        reverse_trace_ref="RT-1",
        evidence_matches_claim=True,
    )
    result = evaluate_adversarial_attempt(attempt)
    assert result.public_judgment == "certificate"
    assert result.blocked_reasons == []


def test_forbidden_transition_blocks_certification():
    attempt = AdversarialAttempt(
        attempt_id="ATT-003",
        requested_judgment="certificate",
        proof_object_ref="PO-2",
        governance_gate_passed=True,
        reverse_trace_ref="RT-2",
        evidence_matches_claim=True,
        transition_tags=["model_output_as_evidence"],
    )
    result = evaluate_adversarial_attempt(attempt)
    assert result.public_judgment == "hypothesis"
    assert "model_output_as_evidence" in result.blocked_reasons


def test_residual_erasure_emits_residual_marker():
    attempt = AdversarialAttempt(
        attempt_id="ATT-004",
        requested_judgment="certificate",
        proof_object_ref="PO-3",
        governance_gate_passed=True,
        reverse_trace_ref="RT-3",
        evidence_matches_claim=True,
        transition_tags=["residual_erasure"],
        residuals=[],
    )
    result = evaluate_adversarial_attempt(attempt)
    assert result.public_judgment == "hypothesis"
    assert "residual_erasure" in result.blocked_reasons
    assert "residual_missing_detected" in result.residuals
