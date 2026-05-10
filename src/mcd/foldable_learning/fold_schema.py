"""FoldSignature dataclass — Phase 7.2."""
from __future__ import annotations
from dataclasses import dataclass, field

__all__ = ["FoldSignature"]


@dataclass
class FoldSignature:
    fold_id: str
    residual_types: list[str] = field(default_factory=list)
    graph_shape: str = ""
    vector_signature: dict = field(default_factory=dict)
    domain_signature: list[str] = field(default_factory=list)
    evidence_signature: str = "source_required"
    certainty_signature: str = "suspend"
    trace_signature: str = "trace_required"
    forbidden_confusions: list[str] = field(default_factory=list)
    recall_keys: list[str] = field(default_factory=list)
    unfold_plan: list[str] = field(default_factory=list)
    learning_actions: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    severity: str = "medium"

    def to_dict(self) -> dict:
        return {
            "fold_id": self.fold_id,
            "residual_types": self.residual_types,
            "graph_shape": self.graph_shape,
            "vector_signature": self.vector_signature,
            "domain_signature": self.domain_signature,
            "evidence_signature": self.evidence_signature,
            "certainty_signature": self.certainty_signature,
            "trace_signature": self.trace_signature,
            "forbidden_confusions": self.forbidden_confusions,
            "recall_keys": self.recall_keys,
            "unfold_plan": self.unfold_plan,
            "learning_actions": self.learning_actions,
            "examples": self.examples,
            "counterexamples": self.counterexamples,
            "metadata": self.metadata,
            "severity": self.severity,
        }
