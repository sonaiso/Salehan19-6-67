"""LearningActionRouter — routes residuals to learning actions."""
from __future__ import annotations
from mcd.residual_learning.residual_schema import CognitiveResidual, Severity
from mcd.residual_learning.learning_action import LearningAction, ActionType
from .fold_schema import FoldSignature

__all__ = ["LearningActionRouter"]

_BLOCKING_ACTIONS = [ActionType.ADD_REGRESSION_TEST, ActionType.ADD_ADVERSARIAL_EXAMPLE, ActionType.REQUIRE_HUMAN_REVIEW]
_HIGH_ACTIONS = [ActionType.ADD_ADVERSARIAL_EXAMPLE, ActionType.ADJUST_CALIBRATION]
_MEDIUM_ACTIONS = [ActionType.ADD_CURRICULUM_EXAMPLE]

_GPT_EVIDENCE_ACTIONS = [ActionType.REJECT_PROPOSAL, ActionType.ADD_REGRESSION_TEST, ActionType.REQUIRE_HUMAN_REVIEW]


class LearningActionRouter:
    def route(self, residual: CognitiveResidual, fold: FoldSignature | None = None) -> list[LearningAction]:
        actions = []

        # Special case: gpt_as_evidence → reject
        if "gpt_as_evidence_residual" in residual.residual_types:
            for at in _GPT_EVIDENCE_ACTIONS:
                actions.append(LearningAction.make(
                    residual_id=residual.residual_id,
                    action_type=at,
                    target_path=f"data/foldable_learning/residual_{residual.residual_id}.json",
                    requires_human_review=(at == ActionType.REQUIRE_HUMAN_REVIEW),
                    reason="GPT output used as evidence — blocking residual",
                ))
            return actions

        sev = residual.severity
        if sev == Severity.BLOCKING.value:
            action_types = _BLOCKING_ACTIONS
        elif sev == Severity.HIGH.value:
            action_types = _HIGH_ACTIONS
        else:
            action_types = _MEDIUM_ACTIONS

        for at in action_types:
            actions.append(LearningAction.make(
                residual_id=residual.residual_id,
                action_type=at,
                target_path=f"data/foldable_learning/residual_{residual.residual_id}.json",
                requires_human_review=(at == ActionType.REQUIRE_HUMAN_REVIEW),
                reason=f"Residual severity={sev}, types={residual.residual_types}",
            ))

        # Pattern memory action for any residual with types
        if residual.residual_types:
            actions.append(LearningAction.make(
                residual_id=residual.residual_id,
                action_type=ActionType.ADD_GOLDEN_CANDIDATE,
                target_path="data/foldable_learning/pattern_memory_seed_ar.jsonl",
                reason="Add fold pattern to memory",
            ))

        return actions

    def batch_route(self, residuals: list[CognitiveResidual]) -> list[LearningAction]:
        all_actions = []
        # Count residual types for invariant proposals
        type_counts: dict[str, int] = {}
        for r in residuals:
            for rt in r.residual_types:
                type_counts[rt] = type_counts.get(rt, 0) + 1

        for residual in residuals:
            all_actions.extend(self.route(residual))

        # Propose invariants for repeated types (>= 3)
        for rt, count in type_counts.items():
            if count >= 3:
                all_actions.append(LearningAction.make(
                    residual_id="BATCH",
                    action_type=ActionType.PROPOSE_INVARIANT,
                    target_path="data/foldable_learning/residual_patterns_ar.jsonl",
                    payload={"residual_type": rt, "frequency": count},
                    reason=f"Residual type {rt} appeared {count} times — propose invariant",
                ))

        return all_actions
