"""LearningAction and ActionType — Phase 7."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class ActionType(str, Enum):
    ADD_CURRICULUM_EXAMPLE = "add_curriculum_example"
    ADD_ADVERSARIAL_EXAMPLE = "add_adversarial_example"
    ADD_REGRESSION_TEST = "add_regression_test"
    PROPOSE_INVARIANT = "propose_invariant"
    ADJUST_CALIBRATION = "adjust_calibration"
    ADD_GOLDEN_CANDIDATE = "add_golden_candidate"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    REJECT_PROPOSAL = "reject_proposal"


@dataclass
class LearningAction:
    """An action derived from a CognitiveResidual."""
    action_id: str
    residual_id: str
    action_type: str
    target_path: str
    payload: dict = field(default_factory=dict)
    requires_human_review: bool = False
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "residual_id": self.residual_id,
            "action_type": self.action_type,
            "target_path": self.target_path,
            "payload": self.payload,
            "requires_human_review": self.requires_human_review,
            "reason": self.reason,
        }

    @classmethod
    def make(
        cls,
        residual_id: str,
        action_type: ActionType,
        target_path: str,
        payload: dict | None = None,
        requires_human_review: bool = False,
        reason: str = "",
    ) -> "LearningAction":
        return cls(
            action_id=str(uuid.uuid4()),
            residual_id=residual_id,
            action_type=action_type.value,
            target_path=target_path,
            payload=payload or {},
            requires_human_review=requires_human_review,
            reason=reason,
        )
