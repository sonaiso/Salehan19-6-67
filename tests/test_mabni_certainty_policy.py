"""Tests for MabniCertaintyPolicy."""
from __future__ import annotations

import pytest
from mcd.mabni.mabni_certainty_policy import MabniCertaintyPolicy
from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction


@pytest.fixture
def policy():
    return MabniCertaintyPolicy()


def _make_op(**kwargs):
    defaults = dict(
        operator_id="TEST",
        surface="ما",
        normalized="ما",
        mabni_type=MabniType.negation,
        logical_function=LogicalFunction.negation,
        pragmatic_function=PragmaticFunction.assertion,
        certainty_effect=CertaintyEffect.lower,
        creates_evidence=False,
        affects_evidence=True,
        affects_certainty=True,
        trace_ids=[],
        examples=[],
    )
    defaults.update(kwargs)
    return MabniOperator(**defaults)


def test_interrogative_suspends(policy):
    op = _make_op(operator_id="Q1", mabni_type=MabniType.interrogative, pragmatic_function=PragmaticFunction.question)
    result = policy.evaluate(op)
    assert result.certainty_policy == "request_evidence"
    assert result.decision_effect == "suspend_judgment"


def test_conditional_suspends(policy):
    op = _make_op(operator_id="C1", mabni_type=MabniType.conditional, logical_function=LogicalFunction.condition)
    result = policy.evaluate(op)
    assert result.certainty_policy == "conditional_certainty"


def test_negation_lowers_certainty(policy):
    op = _make_op(operator_id="N1", mabni_type=MabniType.negation, logical_function=LogicalFunction.negation)
    result = policy.evaluate(op)
    assert result.certainty_policy == "lower_certainty"


def test_emphasis_no_change(policy):
    op = _make_op(
        operator_id="E1",
        mabni_type=MabniType.emphasis,
        logical_function=LogicalFunction.emphasis,
        certainty_effect=CertaintyEffect.emphasis_only,
    )
    result = policy.evaluate(op)
    assert result.certainty_policy == "emphasis_only"
    assert result.decision_effect == "no_certainty_change"


def test_to_dict(policy):
    op = _make_op(operator_id="D1")
    result = policy.evaluate(op)
    d = result.to_dict()
    assert "certainty_policy" in d
    assert "decision_effect" in d
