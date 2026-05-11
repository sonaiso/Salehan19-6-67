"""Tests for LearningActionRouter."""
import pytest
from mcd.foldable_learning.learning_action_router import LearningActionRouter
from mcd.residual_learning.residual_schema import CognitiveResidual


def _make_residual(types, severity="medium"):
    return CognitiveResidual(residual_id="r1", proposal_id="p1", residual_types=types, severity=severity)


def test_gpt_as_evidence_always_rejected():
    router = LearningActionRouter()
    r = _make_residual(["gpt_as_evidence_residual"])
    actions = router.route(r)
    action_types = [a.action_type for a in actions]
    assert "reject_proposal" in action_types


def test_gpt_as_evidence_triggers_human_review():
    router = LearningActionRouter()
    r = _make_residual(["gpt_as_evidence_residual"])
    actions = router.route(r)
    action_types = [a.action_type for a in actions]
    assert "require_human_review" in action_types


def test_gpt_as_evidence_triggers_regression_test():
    router = LearningActionRouter()
    r = _make_residual(["gpt_as_evidence_residual"])
    actions = router.route(r)
    action_types = [a.action_type for a in actions]
    assert "add_regression_test" in action_types


def test_blocking_harm_haram_triggers_human_review():
    router = LearningActionRouter()
    r = _make_residual(["harm_haram_residual"], severity="blocking")
    actions = router.route(r)
    action_types = [a.action_type for a in actions]
    assert "require_human_review" in action_types


def test_batch_route_proposes_invariant():
    router = LearningActionRouter()
    residuals = [_make_residual(["evidence_residual"], "medium") for _ in range(3)]
    all_actions = router.batch_route(residuals)
    all_types = [a.action_type for a in all_actions]
    assert "propose_invariant" in all_types


def test_low_severity_returns_action():
    router = LearningActionRouter()
    r = _make_residual(["metaphor_residual"], severity="low")
    actions = router.route(r)
    assert actions
