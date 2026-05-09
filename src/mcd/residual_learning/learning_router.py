"""LearningRouter — routes CognitiveResiduals to LearningActions.

Rules:
  blocking → add_regression_test + add_adversarial_example + require_human_review
  high     → add_adversarial_example + adjust_calibration
  medium   → add_curriculum_example
  low      → add_golden_candidate (or ignore)

Does NOT write directly to golden dataset unless human_review=True or approved flag.
"""
from __future__ import annotations

from .residual_schema import CognitiveResidual, Severity
from .residual_classifier import ResidualClassifier, ResidualClassification
from .learning_action import LearningAction, ActionType

_DATA_ROOT = "data/residual_learning"


class LearningRouter:
    """Routes a residual to one or more LearningActions."""

    def __init__(self) -> None:
        self._classifier = ResidualClassifier()

    def route(self, residual: CognitiveResidual) -> list[LearningAction]:
        classification = self._classifier.classify(residual)
        return self._build_actions(residual, classification)

    def _build_actions(
        self,
        residual: CognitiveResidual,
        cls: ResidualClassification,
    ) -> list[LearningAction]:
        actions: list[LearningAction] = []
        rid = residual.residual_id
        sev = residual.severity

        if sev == Severity.BLOCKING.value:
            actions.append(LearningAction.make(
                rid,
                ActionType.ADD_REGRESSION_TEST,
                target_path=f"{_DATA_ROOT}/generated_regression_tests.jsonl",
                reason=f"Blocking residual types: {residual.residual_types}",
            ))
            actions.append(LearningAction.make(
                rid,
                ActionType.ADD_ADVERSARIAL_EXAMPLE,
                target_path=f"{_DATA_ROOT}/generated_adversarial.jsonl",
                reason="Blocking residuals must create adversarial candidates.",
            ))
            actions.append(LearningAction.make(
                rid,
                ActionType.REQUIRE_HUMAN_REVIEW,
                target_path="human_review_queue",
                requires_human_review=True,
                reason="Blocking residual requires human review before any core update.",
            ))

        elif sev == Severity.HIGH.value:
            actions.append(LearningAction.make(
                rid,
                ActionType.ADD_ADVERSARIAL_EXAMPLE,
                target_path=f"{_DATA_ROOT}/generated_adversarial.jsonl",
                reason=f"High residual: {residual.residual_types}",
            ))
            actions.append(LearningAction.make(
                rid,
                ActionType.ADJUST_CALIBRATION,
                target_path=f"{_DATA_ROOT}/generated_calibration_updates.jsonl",
                reason="High residual triggers calibration adjustment recommendation.",
            ))

        elif sev == Severity.MEDIUM.value:
            actions.append(LearningAction.make(
                rid,
                ActionType.ADD_CURRICULUM_EXAMPLE,
                target_path=f"{_DATA_ROOT}/generated_curriculum_examples.jsonl",
                reason=f"Medium residual: {residual.residual_types}",
            ))

        else:  # low
            actions.append(LearningAction.make(
                rid,
                ActionType.ADD_GOLDEN_CANDIDATE,
                target_path=f"{_DATA_ROOT}/generated_golden_candidates.jsonl",
                requires_human_review=True,
                reason="Low residual — golden candidate for human review.",
            ))

        # Propose invariant if there are invariant violations
        for inv in residual.invariant_violations:
            actions.append(LearningAction.make(
                rid,
                ActionType.PROPOSE_INVARIANT,
                target_path=f"{_DATA_ROOT}/generated_invariant_proposals.jsonl",
                payload={"invariant": inv},
                requires_human_review=True,
                reason=f"Invariant violation detected: {inv}",
            ))

        return actions
