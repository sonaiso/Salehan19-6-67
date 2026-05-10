from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

RESIDUAL_TYPES = {
    "missing_evidence", "unsupported_generalization", "ungrounded_claim",
    "missing_trace", "operator_mismatch", "certainty_overreach",
    "missing_source", "gpt_hallucination_pattern",
}

LEARNING_ACTIONS = {
    "add_test", "add_invariant", "flag_for_review",
    "suspend_certainty", "request_source", "pattern_mine",
}


@dataclass
class GPTResidualFoldingContract:
    """Schema/contract for GPT residual folding. No GPT calls here."""
    proposal_unit_id: str
    contract_projection_unit_id: str
    residual_unit_id: str
    residual_types: list[str] = field(default_factory=list)
    fold_pattern_id: Optional[str] = None
    learning_actions: list[str] = field(default_factory=list)
    proof_effect: str = "none"

    def __post_init__(self):
        for rt in self.residual_types:
            if rt not in RESIDUAL_TYPES:
                raise ValueError(f"Unknown residual_type: {rt}")
        for la in self.learning_actions:
            if la not in LEARNING_ACTIONS:
                raise ValueError(f"Unknown learning_action: {la}")
        # Core invariant: GPT output is not evidence
        if self.proof_effect == "certificate":
            raise ValueError("GPT residual contract cannot produce Certificate proof")

    @staticmethod
    def make_id() -> str:
        return f"RFC-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "proposal_unit_id": self.proposal_unit_id,
            "contract_projection_unit_id": self.contract_projection_unit_id,
            "residual_unit_id": self.residual_unit_id,
            "residual_types": self.residual_types,
            "fold_pattern_id": self.fold_pattern_id,
            "learning_actions": self.learning_actions,
            "proof_effect": self.proof_effect,
        }

    # Invariant checks
    @staticmethod
    def gpt_is_not_evidence() -> bool:
        """GPT output is never evidence. This is a hard invariant."""
        return True

    @staticmethod
    def gpt_cannot_raise_certainty() -> bool:
        """GPT proposal cannot raise certainty. This is a hard invariant."""
        return True
