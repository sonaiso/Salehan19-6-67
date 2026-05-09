"""Tests for LearningRouter."""
from __future__ import annotations

import pytest
from mcd.residual_learning.residual_schema import CognitiveResidual, ResidualType, Severity
from mcd.residual_learning.learning_action import ActionType
from mcd.residual_learning.learning_router import LearningRouter


def make_residual(
    types: list[str],
    severity: str,
    invariant_violations: list[str] | None = None,
) -> CognitiveResidual:
    return CognitiveResidual(
        residual_id="router-test",
        proposal_id="p-001",
        residual_types=types,
        severity=severity,
        invariant_violations=invariant_violations or [],
        residual_score=0.5,
        explanation="Test",
    )


class TestLearningRouter:
    def setup_method(self) -> None:
        self.router = LearningRouter()

    def test_blocking_residual_requires_human_review(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)
        actions = self.router.route(r)
        review_actions = [a for a in actions if a.action_type == ActionType.REQUIRE_HUMAN_REVIEW.value]
        assert len(review_actions) > 0
        assert all(a.requires_human_review for a in review_actions)

    def test_blocking_creates_regression_test(self) -> None:
        r = make_residual([ResidualType.INJECTION.value], Severity.BLOCKING.value)
        actions = self.router.route(r)
        reg_actions = [a for a in actions if a.action_type == ActionType.ADD_REGRESSION_TEST.value]
        assert len(reg_actions) > 0

    def test_blocking_creates_adversarial_example(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)
        actions = self.router.route(r)
        adv_actions = [a for a in actions if a.action_type == ActionType.ADD_ADVERSARIAL_EXAMPLE.value]
        assert len(adv_actions) > 0

    def test_high_creates_adversarial_and_calibration(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value], Severity.HIGH.value)
        actions = self.router.route(r)
        types = {a.action_type for a in actions}
        assert ActionType.ADD_ADVERSARIAL_EXAMPLE.value in types
        assert ActionType.ADJUST_CALIBRATION.value in types

    def test_medium_creates_curriculum_example(self) -> None:
        r = make_residual([ResidualType.METAPHOR.value], Severity.MEDIUM.value)
        actions = self.router.route(r)
        cur_actions = [a for a in actions if a.action_type == ActionType.ADD_CURRICULUM_EXAMPLE.value]
        assert len(cur_actions) > 0

    def test_low_creates_golden_candidate(self) -> None:
        r = make_residual([ResidualType.VECTOR.value], Severity.LOW.value)
        actions = self.router.route(r)
        gold_actions = [a for a in actions if a.action_type == ActionType.ADD_GOLDEN_CANDIDATE.value]
        assert len(gold_actions) > 0

    def test_golden_candidate_requires_human_review(self) -> None:
        r = make_residual([ResidualType.VECTOR.value], Severity.LOW.value)
        actions = self.router.route(r)
        gold_actions = [a for a in actions if a.action_type == ActionType.ADD_GOLDEN_CANDIDATE.value]
        assert all(a.requires_human_review for a in gold_actions)

    def test_invariant_violation_proposes_invariant(self) -> None:
        r = make_residual(
            [ResidualType.HARM_HARAM.value],
            Severity.BLOCKING.value,
            invariant_violations=["harm_haram_invariant"],
        )
        actions = self.router.route(r)
        inv_actions = [a for a in actions if a.action_type == ActionType.PROPOSE_INVARIANT.value]
        assert len(inv_actions) > 0
        assert inv_actions[0].payload.get("invariant") == "harm_haram_invariant"

    def test_all_actions_have_target_path(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value], Severity.HIGH.value)
        actions = self.router.route(r)
        for action in actions:
            assert action.target_path

    def test_all_actions_are_json_serializable(self) -> None:
        import json
        r = make_residual([ResidualType.TOOL_EVIDENCE.value], Severity.HIGH.value)
        actions = self.router.route(r)
        for action in actions:
            json.dumps(action.to_dict())  # should not raise
