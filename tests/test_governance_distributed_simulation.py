from __future__ import annotations

from mcd.governance.adversarial_validation import AdversarialAttempt
from mcd.governance.distributed_simulation import (
    DistributedAgentAttempt,
    run_distributed_governance_simulation,
)


def test_distributed_simulation_reports_consistent_summary():
    attempts = [
        DistributedAgentAttempt(
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="A-1",
                requested_judgment="certificate",
                proof_object_ref="PO-1",
                governance_gate_passed=True,
                reverse_trace_ref="RT-1",
                evidence_matches_claim=True,
            ),
        ),
        DistributedAgentAttempt(
            agent_id="agent-b",
            attempt=AdversarialAttempt(
                attempt_id="B-1",
                requested_judgment="certificate",
                proof_object_ref="",
                governance_gate_passed=False,
                reverse_trace_ref="",
                evidence_matches_claim=False,
            ),
        ),
        DistributedAgentAttempt(
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="A-2",
                requested_judgment="zero",
            ),
        ),
    ]
    result = run_distributed_governance_simulation(attempts)
    summary = result.summary()

    assert summary["total_attempts"] == 3
    assert summary["judgment_counts"]["certificate"] == 1
    assert summary["judgment_counts"]["hypothesis"] == 1
    assert summary["judgment_counts"]["zero"] == 1
    assert result.consistency_ok
    assert set(result.evaluations_by_agent.keys()) == {"agent-a", "agent-b"}


def test_distributed_simulation_detects_blocking_residual_erasure():
    attempts = [
        DistributedAgentAttempt(
            agent_id="agent-x",
            attempt=AdversarialAttempt(
                attempt_id="X-1",
                requested_judgment="certificate",
                proof_object_ref="PO-9",
                governance_gate_passed=True,
                reverse_trace_ref="RT-9",
                evidence_matches_claim=True,
                residuals=["residual_conflict"],
            ),
        )
    ]
    result = run_distributed_governance_simulation(attempts)
    summary = result.summary()

    assert summary["judgment_counts"]["certificate"] == 0
    assert summary["judgment_counts"]["hypothesis"] == 1
    assert result.consistency_ok
