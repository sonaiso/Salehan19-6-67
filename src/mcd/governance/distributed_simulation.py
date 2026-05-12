"""Distributed governance simulation for multi-agent certification attempts."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.governance.adversarial_validation import (
    AdversarialAttempt,
    AdversarialEvaluation,
    evaluate_adversarial_attempt,
)


@dataclass
class DistributedAgentAttempt:
    agent_id: str
    attempt: AdversarialAttempt


@dataclass
class DistributedSimulationResult:
    evaluations: list[AdversarialEvaluation] = field(default_factory=list)
    evaluations_by_agent: dict[str, list[AdversarialEvaluation]] = field(default_factory=dict)
    consistency_ok: bool = True
    consistency_violations: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        counts = {"zero": 0, "hypothesis": 0, "certificate": 0}
        for evaluation in self.evaluations:
            counts[evaluation.public_judgment] += 1
        return {
            "total_attempts": len(self.evaluations),
            "judgment_counts": counts,
            "consistency_ok": self.consistency_ok,
            "consistency_violations": list(self.consistency_violations),
        }


def _validate_evaluation(evaluation: AdversarialEvaluation) -> list[str]:
    violations: list[str] = []
    if evaluation.public_judgment not in {"zero", "hypothesis", "certificate"}:
        violations.append(f"{evaluation.attempt_id}: non-canonical-judgment")
    if evaluation.blocked_reasons and evaluation.public_judgment == "certificate":
        violations.append(f"{evaluation.attempt_id}: certificate-with-blockers")
    if "blocking_residual_present" in evaluation.blocked_reasons and not evaluation.residuals:
        violations.append(f"{evaluation.attempt_id}: residual-erasure")
    return violations


def run_distributed_governance_simulation(
    attempts: list[DistributedAgentAttempt],
) -> DistributedSimulationResult:
    evaluations: list[AdversarialEvaluation] = []
    evaluations_by_agent: dict[str, list[AdversarialEvaluation]] = {}
    violations: list[str] = []

    for item in attempts:
        evaluation = evaluate_adversarial_attempt(item.attempt)
        evaluations.append(evaluation)
        evaluations_by_agent.setdefault(item.agent_id, []).append(evaluation)
        violations.extend(_validate_evaluation(evaluation))

    return DistributedSimulationResult(
        evaluations=evaluations,
        evaluations_by_agent=evaluations_by_agent,
        consistency_ok=not violations,
        consistency_violations=violations,
    )
