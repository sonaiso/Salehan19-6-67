"""JudgmentTrace — the final judgment with full trace chain."""
from __future__ import annotations

from dataclasses import dataclass, field

FINAL_DECISIONS = ["answer", "suspend", "request_evidence", "reject", "escalate"]


@dataclass
class JudgmentTrace:
    judgment_id: str
    input_text: str
    unicode_trace_ids: list[str]
    token_ids: list[str]
    node_ids: list[str]
    edge_ids: list[str]
    vector_ids: list[str]
    evidence_status: str
    certainty_policy: str
    final_decision: str
    warnings: list[str]
    explanation: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.final_decision not in FINAL_DECISIONS:
            raise ValueError(f"Invalid final_decision '{self.final_decision}'")

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "input_text": self.input_text,
            "unicode_trace_ids": self.unicode_trace_ids,
            "token_ids": self.token_ids,
            "node_ids": self.node_ids,
            "edge_ids": self.edge_ids,
            "vector_ids": self.vector_ids,
            "evidence_status": self.evidence_status,
            "certainty_policy": self.certainty_policy,
            "final_decision": self.final_decision,
            "warnings": self.warnings,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }
