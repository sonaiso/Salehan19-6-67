from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GovernedFractalUnit:
    unit_id: str
    level_id: str
    unit_type: str
    surface: str = ""
    normalized: str = ""
    pre_unit_ids: list[str] = field(default_factory=list)
    post_unit_ids: list[str] = field(default_factory=list)
    morphism_in: str | None = None
    morphism_out: str | None = None
    vector: dict[str, float] = field(default_factory=dict)
    relations: list[dict[str, str]] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    evidence_state: str = "missing"
    certainty_state: str = "suspend"
    proof_state: str = "none"
    trace_refs: list[str] = field(default_factory=list)
    residual_refs: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_generated(self) -> bool:
        return bool(self.metadata.get("generated") or self.metadata.get("generated_reason"))

    def validate(self, final_pipeline: bool = False) -> list[str]:
        violations: list[str] = []
        if not self.pre_unit_ids and not self.is_generated():
            violations.append(f"{self.unit_id}: missing pre_unit_ids or generated_reason")
        if final_pipeline and not self.post_unit_ids:
            violations.append(f"{self.unit_id}: missing post_unit_ids for final pipeline")
        if not self.trace_refs and not self.is_generated():
            violations.append(f"{self.unit_id}: trace_refs are required unless generated")
        if not self.level_id:
            violations.append(f"{self.unit_id}: level_id is required")
        if not self.unit_type:
            violations.append(f"{self.unit_id}: unit_type is required")
        return violations

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "level_id": self.level_id,
            "unit_type": self.unit_type,
            "surface": self.surface,
            "normalized": self.normalized,
            "pre_unit_ids": self.pre_unit_ids,
            "post_unit_ids": self.post_unit_ids,
            "morphism_in": self.morphism_in,
            "morphism_out": self.morphism_out,
            "vector": self.vector,
            "relations": self.relations,
            "operators": self.operators,
            "evidence_state": self.evidence_state,
            "certainty_state": self.certainty_state,
            "proof_state": self.proof_state,
            "trace_refs": self.trace_refs,
            "residual_refs": self.residual_refs,
            "invariants": self.invariants,
            "metadata": self.metadata,
        }
