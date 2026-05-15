"""Tests for ConceptClaim governance evaluator."""
from __future__ import annotations

import pytest

from mcd.nabhani.concept_claim_governance_evaluator import ConceptClaim, ConceptClaimGovernanceEvaluator


@pytest.fixture
def evaluator():
    return ConceptClaimGovernanceEvaluator()


def _base_claim(**overrides):
    claim = ConceptClaim(
        claim="Water boils at 100C under standard pressure.",
        domain="scientific_experimental",
        topic="material",
        thinking_type="deep",
        reality_anchor="lab observation",
        sensation_path="experiment",
        prior_information=["boiling point basics"],
        governing_measure="experimental",
        certainty_level="hypothesis",
        evidence_refs=["exp-001"],
        reverse_trace_ref=None,
    )
    return ConceptClaim(**{**claim.__dict__, **overrides})


def test_accepts_when_all_required_gates_pass(evaluator):
    decision = evaluator.evaluate(_base_claim())
    assert decision.status == "accepted"
    assert decision.can_issue_certificate is False
    assert decision.residuals == []


def test_rejects_when_reality_anchor_missing(evaluator):
    decision = evaluator.evaluate(_base_claim(reality_anchor=None))
    assert decision.status == "rejected"
    assert "missing_reality_anchor" in decision.residuals


def test_marks_misclassified_on_domain_topic_mismatch(evaluator):
    decision = evaluator.evaluate(_base_claim(topic="legislation"))
    assert decision.status == "misclassified"
    assert "domain_topic_mismatch" in decision.residuals


def test_marks_invalid_measure_when_measure_not_allowed_for_domain(evaluator):
    decision = evaluator.evaluate(_base_claim(governing_measure="scriptural"))
    assert decision.status == "invalid_measure"
    assert "invalid_governing_measure" in decision.residuals


def test_certificate_needs_reverse_trace_when_requested(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            certainty_level="CERTIFICATE",
            evidence_refs=["exp-001", "exp-002"],
            reverse_trace_ref=None,
        )
    )
    assert decision.status == "needs_evidence"
    assert decision.can_issue_certificate is False
    assert "reverse_trace_missing" in decision.residuals
    assert "certificate_not_allowed" in decision.residuals


def test_certificate_blocked_on_certainty_overclaim(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            certainty_level="certificate",
            evidence_refs=["exp-001"],
            reverse_trace_ref="rt-1",
        )
    )
    assert decision.status == "needs_evidence"
    assert "certainty_overclaim" in decision.residuals
    assert "certificate_not_allowed" in decision.residuals
    assert decision.can_issue_certificate is False


def test_certificate_allowed_only_when_all_certificate_conditions_pass(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            certainty_level="CERTIFICATE",
            evidence_refs=["exp-001", "exp-002"],
            reverse_trace_ref="rt-1",
        )
    )
    assert decision.status == "accepted"
    assert decision.can_issue_certificate is True
    assert decision.residuals == []
