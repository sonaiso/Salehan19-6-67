from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

VALID_LEVELS = {
    "unicode", "grapheme", "token", "root", "pattern", "word",
    "mabni", "murab", "phrase", "sentence", "concept",
    "judgment", "proof", "residual", "fold_pattern"
}

VALID_FOLD_STATES = {"atomic", "folded", "unfolded", "refolded"}

@dataclass
class CognitiveFractalUnit:
    unit_id: str
    level: str
    unit_type: str
    surface: Optional[str] = None
    normalized: Optional[str] = None
    vector_refs: list[str] = field(default_factory=list)
    operator_refs: list[str] = field(default_factory=list)
    relation_refs: list[str] = field(default_factory=list)
    parent_unit_ids: list[str] = field(default_factory=list)
    child_unit_ids: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    certainty_state: str = "unknown"
    proof_refs: list[str] = field(default_factory=list)
    fold_state: str = "atomic"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.unit_id:
            raise ValueError("unit_id is required")
        if self.level not in VALID_LEVELS:
            raise ValueError(f"Invalid level: {self.level}. Must be one of {VALID_LEVELS}")
        if not self.unit_type:
            raise ValueError("unit_type is required")
        if self.fold_state not in VALID_FOLD_STATES:
            raise ValueError(f"Invalid fold_state: {self.fold_state}")

    @staticmethod
    def make_id(prefix: str = "CFU") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "level": self.level,
            "unit_type": self.unit_type,
            "surface": self.surface,
            "normalized": self.normalized,
            "vector_refs": self.vector_refs,
            "operator_refs": self.operator_refs,
            "relation_refs": self.relation_refs,
            "parent_unit_ids": self.parent_unit_ids,
            "child_unit_ids": self.child_unit_ids,
            "trace_refs": self.trace_refs,
            "evidence_refs": self.evidence_refs,
            "certainty_state": self.certainty_state,
            "proof_refs": self.proof_refs,
            "fold_state": self.fold_state,
            "metadata": self.metadata,
        }
