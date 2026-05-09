"""CognitiveResidual schema — Phase 7."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class ResidualType(str, Enum):
    STRUCTURAL = "structural_residual"
    EDGE = "edge_residual"
    VECTOR = "vector_residual"
    EVIDENCE = "evidence_residual"
    CERTAINTY = "certainty_residual"
    DOMAIN = "domain_residual"
    CAUSALITY = "causality_residual"
    METAPHOR = "metaphor_residual"
    TOOL_EVIDENCE = "tool_evidence_residual"
    HARM_HARAM = "harm_haram_residual"
    INJECTION = "injection_residual"
    AMBIGUITY = "ambiguity_residual"
    UNSUPPORTED_GENERALIZATION = "unsupported_generalization_residual"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKING = "blocking"


@dataclass
class CognitiveResidual:
    """The mathematical difference between a GPTProposal and the MathematicalContract.

    residual = GPTProposal − MathematicalContract

    Residual is a *learning signal*, not a final truth.
    """
    residual_id: str
    proposal_id: str
    residual_types: list[str] = field(default_factory=list)
    missing_nodes: list[str] = field(default_factory=list)
    missing_edges: list[str] = field(default_factory=list)
    invalid_edges: list[str] = field(default_factory=list)
    vector_deviations: dict[str, float] = field(default_factory=dict)
    evidence_gaps: list[str] = field(default_factory=list)
    certainty_errors: list[str] = field(default_factory=list)
    domain_errors: list[str] = field(default_factory=list)
    causality_errors: list[str] = field(default_factory=list)
    metaphor_errors: list[str] = field(default_factory=list)
    safety_errors: list[str] = field(default_factory=list)
    invariant_violations: list[str] = field(default_factory=list)
    severity: str = Severity.LOW.value
    residual_score: float = 0.0
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "residual_id": self.residual_id,
            "proposal_id": self.proposal_id,
            "residual_types": self.residual_types,
            "missing_nodes": self.missing_nodes,
            "missing_edges": self.missing_edges,
            "invalid_edges": self.invalid_edges,
            "vector_deviations": self.vector_deviations,
            "evidence_gaps": self.evidence_gaps,
            "certainty_errors": self.certainty_errors,
            "domain_errors": self.domain_errors,
            "causality_errors": self.causality_errors,
            "metaphor_errors": self.metaphor_errors,
            "safety_errors": self.safety_errors,
            "invariant_violations": self.invariant_violations,
            "severity": self.severity,
            "residual_score": round(self.residual_score, 4),
            "explanation": self.explanation,
        }

    @classmethod
    def make_empty(cls, proposal_id: str) -> "CognitiveResidual":
        return cls(
            residual_id=str(uuid.uuid4()),
            proposal_id=proposal_id,
            severity=Severity.LOW.value,
            residual_score=0.0,
            explanation="No residual detected — proposal passed all contract checks.",
        )
