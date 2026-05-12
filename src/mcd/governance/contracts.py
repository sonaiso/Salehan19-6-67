"""Canonical governance contracts shared across runtimes."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CanonicalGovernanceRecord:
    runtime: str
    judgment: str
    proof_object_ref: str
    governance_gate_passed: bool
    reverse_trace_ref: str
    trace_graph_ref: str
    legitimacy_state: str
    rank_calculus_state: str
    residuals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "runtime": self.runtime,
            "judgment": self.judgment,
            "proof_object_ref": self.proof_object_ref,
            "governance_gate_passed": self.governance_gate_passed,
            "reverse_trace_ref": self.reverse_trace_ref,
            "trace_graph_ref": self.trace_graph_ref,
            "legitimacy_state": self.legitimacy_state,
            "rank_calculus_state": self.rank_calculus_state,
            "residuals": list(self.residuals),
        }

