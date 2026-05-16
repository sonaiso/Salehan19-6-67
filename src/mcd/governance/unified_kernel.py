"""Unified governance kernel contract and mapping helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.governance.contracts import CanonicalGovernanceRecord


@dataclass
class UnifiedGovernanceKernel:
    Input: dict[str, Any]
    Candidates: list[dict[str, Any]]
    Constraints: list[dict[str, Any]]
    Evidence: list[dict[str, Any]]
    Residuals: list[str] = field(default_factory=list)
    Decision: dict[str, Any] = field(default_factory=dict)
    Trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "Input": self.Input,
            "Candidates": self.Candidates,
            "Constraints": self.Constraints,
            "Evidence": self.Evidence,
            "Residuals": list(self.Residuals),
            "Decision": self.Decision,
            "Trace": self.Trace,
        }


def from_canonical_record(record: CanonicalGovernanceRecord) -> UnifiedGovernanceKernel:
    """Project canonical runtime governance record into unified kernel shape."""
    blocked = not record.governance_gate_passed
    constraints = [
        {
            "id": "governance_gate",
            "passed": record.governance_gate_passed,
            "reason": "governance_gate_passed",
        }
    ]
    evidence = []
    if record.proof_object_ref:
        evidence.append({"type": "proof_object_ref", "ref": record.proof_object_ref})

    return UnifiedGovernanceKernel(
        Input={
            "runtime": record.runtime,
            "trace_graph_ref": record.trace_graph_ref,
            "legitimacy_state": record.legitimacy_state,
            "rank_calculus_state": record.rank_calculus_state,
        },
        Candidates=[
            {
                "judgment": record.judgment,
                "certificate_candidate": record.judgment == "certificate",
            }
        ],
        Constraints=constraints,
        Evidence=evidence,
        Residuals=list(record.residuals),
        Decision={
            "judgment": record.judgment,
            "governance_gate_passed": record.governance_gate_passed,
            "certificate_allowed": record.judgment == "certificate" and not blocked,
        },
        Trace={
            "proof_object_ref": record.proof_object_ref,
            "reverse_trace_ref": record.reverse_trace_ref,
            "reverse_trace_complete": bool(record.reverse_trace_ref),
        },
    )

