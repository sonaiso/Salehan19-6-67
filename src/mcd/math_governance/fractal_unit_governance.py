from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_BETA_STATUSES = {"undefined", "invalid", "valid_uncertified", "valid_certified"}


@dataclass
class GovernedFractalUnit:
    unit_id: str
    level_id: str
    unit_type: str
    surface: str = ""
    normalized: str = ""
    raw_span: tuple[int, int] = (0, 0)
    normalized_span: tuple[int, int] = (0, 0)
    raw_text: str = ""
    normalized_text: str = ""
    pre_unit_ids: list[str] = field(default_factory=list)
    post_unit_ids: list[str] = field(default_factory=list)
    morphism_in: str | None = None
    morphism_out: str | None = None
    pre_to_post_relation: str = ""
    vector: dict[str, float] = field(default_factory=dict)
    relations: list[dict[str, str]] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    evidence_state: str = "missing"
    certainty_state: str = "suspend"
    proof_state: str = "none"
    trace_refs: list[str] = field(default_factory=list)
    residual_refs: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    beta_status: str = "undefined"
    invariants: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.raw_text:
            self.raw_text = self.surface
        if not self.normalized_text:
            self.normalized_text = self.normalized or self.surface
        if self.raw_span == (0, 0) and self.raw_text:
            self.raw_span = (0, len(self.raw_text))
        if self.normalized_span == (0, 0) and self.normalized_text:
            self.normalized_span = (0, len(self.normalized_text))
        if not self.residuals and self.residual_refs:
            self.residuals = list(self.residual_refs)

    def is_generated(self) -> bool:
        return bool(self.metadata.get("generated") or self.metadata.get("generated_reason"))

    @staticmethod
    def _valid_span(span: tuple[int, int]) -> bool:
        if not isinstance(span, tuple) or len(span) != 2:
            return False
        a, b = span
        return isinstance(a, int) and isinstance(b, int) and a >= 0 and b >= a

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
        if not self._valid_span(self.raw_span):
            violations.append(f"{self.unit_id}: raw_span must be a valid [start,end] tuple")
        if not self._valid_span(self.normalized_span):
            violations.append(f"{self.unit_id}: normalized_span must be a valid [start,end] tuple")
        if not self.raw_text:
            violations.append(f"{self.unit_id}: raw_text is required")
        if not self.normalized_text:
            violations.append(f"{self.unit_id}: normalized_text is required")
        if final_pipeline and self.post_unit_ids and not self.pre_to_post_relation:
            violations.append(f"{self.unit_id}: pre_to_post_relation is required for outgoing transition")
        if self.beta_status not in VALID_BETA_STATUSES:
            violations.append(
                f"{self.unit_id}: beta_status must be one of {sorted(VALID_BETA_STATUSES)}"
            )
        return violations

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "level_id": self.level_id,
            "unit_type": self.unit_type,
            "surface": self.surface,
            "normalized": self.normalized,
            "raw_span": list(self.raw_span),
            "normalized_span": list(self.normalized_span),
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "pre_unit_ids": self.pre_unit_ids,
            "post_unit_ids": self.post_unit_ids,
            "morphism_in": self.morphism_in,
            "morphism_out": self.morphism_out,
            "pre_to_post_relation": self.pre_to_post_relation,
            "vector": self.vector,
            "relations": self.relations,
            "operators": self.operators,
            "evidence_state": self.evidence_state,
            "certainty_state": self.certainty_state,
            "proof_state": self.proof_state,
            "trace_refs": self.trace_refs,
            "residual_refs": self.residual_refs,
            "residuals": self.residuals,
            "beta_status": self.beta_status,
            "invariants": self.invariants,
            "metadata": self.metadata,
        }
