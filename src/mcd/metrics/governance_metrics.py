"""Governance metrics with optional Prometheus export hooks."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GovernanceMetrics:
    forbidden_transition_rate: float
    certificate_block_rate: float
    residual_integrity: float
    trace_completeness: float
    governance_consistency: float
    replay_success_rate: float
    collapse_frequency: float

    def to_dict(self) -> dict:
        return {
            "forbidden_transition_rate": self.forbidden_transition_rate,
            "certificate_block_rate": self.certificate_block_rate,
            "residual_integrity": self.residual_integrity,
            "trace_completeness": self.trace_completeness,
            "governance_consistency": self.governance_consistency,
            "replay_success_rate": self.replay_success_rate,
            "collapse_frequency": self.collapse_frequency,
        }

    def to_prometheus(self) -> str:
        d = self.to_dict()
        return "\n".join(f"mcd_{k} {v}" for k, v in d.items()) + "\n"


def compute_governance_metrics(events: list[dict]) -> GovernanceMetrics:
    total = max(len(events), 1)
    forbidden = sum(1 for e in events if e.get("forbidden_transition"))
    blocked = sum(1 for e in events if e.get("certificate_blocked"))
    residual_ok = sum(1 for e in events if e.get("residual_preserved", False))
    trace_ok = sum(1 for e in events if e.get("trace_complete", False))
    governance_ok = sum(1 for e in events if e.get("governance_consistent", False))
    replay_ok = sum(1 for e in events if e.get("replay_success", True))
    collapse = sum(1 for e in events if e.get("collapse_event"))
    return GovernanceMetrics(
        forbidden_transition_rate=forbidden / total,
        certificate_block_rate=blocked / total,
        residual_integrity=residual_ok / total,
        trace_completeness=trace_ok / total,
        governance_consistency=governance_ok / total,
        replay_success_rate=replay_ok / total,
        collapse_frequency=collapse / total,
    )

