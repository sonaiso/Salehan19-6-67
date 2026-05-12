from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")
strategies = pytest.importorskip("hypothesis.strategies")

from mcd.governance.adversarial_validation import AdversarialAttempt, evaluate_adversarial_attempt
from mcd.governance.distributed_simulation import (
    DistributedAgentAttempt,
    run_distributed_governance_simulation,
)


@hypothesis.given(strategies.text())
def test_adversarial_public_judgment_always_canonical(requested_judgment: str):
    result = evaluate_adversarial_attempt(
        AdversarialAttempt(
            attempt_id="P-1",
            requested_judgment=requested_judgment,
        )
    )
    assert result.public_judgment in {"zero", "hypothesis", "certificate"}


@hypothesis.given(
    proof_object_ref=strategies.text(max_size=8),
    governance_gate_passed=strategies.booleans(),
    reverse_trace_ref=strategies.text(max_size=8),
    evidence_matches_claim=strategies.booleans(),
)
def test_certificate_never_issued_when_mandatory_gates_missing(
    proof_object_ref: str,
    governance_gate_passed: bool,
    reverse_trace_ref: str,
    evidence_matches_claim: bool,
):
    result = evaluate_adversarial_attempt(
        AdversarialAttempt(
            attempt_id="P-2",
            requested_judgment="certificate",
            proof_object_ref=proof_object_ref,
            governance_gate_passed=governance_gate_passed,
            reverse_trace_ref=reverse_trace_ref,
            evidence_matches_claim=evidence_matches_claim,
        )
    )
    if not proof_object_ref or not governance_gate_passed or not reverse_trace_ref or not evidence_matches_claim:
        assert result.public_judgment != "certificate"


@hypothesis.given(strategies.lists(strategies.sampled_from(["certificate", "hypothesis", "zero", "suspend"])))
def test_distributed_simulation_never_emits_non_canonical_final_judgment(statuses: list[str]):
    attempts = [
        DistributedAgentAttempt(
            agent_id=f"agent-{i % 3}",
            attempt=AdversarialAttempt(
                attempt_id=f"P3-{i}",
                requested_judgment=status,
            ),
        )
        for i, status in enumerate(statuses)
    ]
    result = run_distributed_governance_simulation(attempts)
    assert all(e.public_judgment in {"zero", "hypothesis", "certificate"} for e in result.evaluations)
