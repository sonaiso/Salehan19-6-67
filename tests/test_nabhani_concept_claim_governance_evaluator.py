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
    assert decision.gates["semantic_layer_separation_gate"] is True
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
    assert "invalid_measure_domain" in decision.residuals


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


def test_invalid_measure_topic_residual_is_emitted(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            governing_measure="experimental",
            topic="creed",
        )
    )
    assert "invalid_measure_topic" in decision.residuals


def test_unsupported_data_type_when_representation_type_unknown(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            representation_type="quantum_qualia",
        )
    )
    assert decision.status == "invalid_measure"
    assert "unsupported_data_type" in decision.residuals


def test_metric_extension_fallacy_when_cross_layer_transition_invalid(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            governing_measure="dalala",
            ontological_object_type="event",
            representation_type="causal",
        )
    )
    assert decision.status == "invalid_measure"
    assert "metric_extension_fallacy" in decision.residuals


def test_metric_certainty_capped_when_measure_cannot_issue_certificate(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            governing_measure="dalala",
            domain="rational_general",
            topic="concept",
            ontological_object_type="entity",
            representation_type="linguistic",
            semantic_type="linguistic",
            inference_type="dalala",
            relation_type="linguistic",
            certainty_level="CERTIFICATE",
            evidence_refs=["e1", "e2", "e3"],
            reverse_trace_ref="rt-1",
        )
    )
    assert decision.status == "needs_evidence"
    assert decision.can_issue_certificate is False
    assert "metric_certainty_capped" in decision.residuals


def test_definition_cannot_promote_directly_to_judgment(evaluator):
    decision = evaluator.evaluate(_base_claim(judgment_basis_type="definition"))
    assert decision.status == "invalid_measure"
    assert decision.gates["semantic_layer_separation_gate"] is False
    assert "definition_as_judgment" in decision.residuals
    assert "invalid_semantic_transition" in decision.residuals


def test_interpretation_cannot_promote_directly_to_evidence(evaluator):
    decision = evaluator.evaluate(_base_claim(evidence_basis_type="interpretation"))
    assert decision.status == "invalid_measure"
    assert decision.gates["semantic_layer_separation_gate"] is False
    assert "interpretation_as_evidence" in decision.residuals
    assert "invalid_semantic_transition" in decision.residuals


def test_relation_cannot_promote_directly_to_inference(evaluator):
    decision = evaluator.evaluate(_base_claim(inference_basis_type="relation"))
    assert decision.status == "invalid_measure"
    assert decision.gates["semantic_layer_separation_gate"] is False
    assert "relation_as_inference" in decision.residuals
    assert "invalid_semantic_transition" in decision.residuals


def test_semantic_cannot_promote_to_judgment_without_semantic_inference_gate(evaluator):
    decision = evaluator.evaluate(
        _base_claim(
            governing_measure="dalala",
            domain="rational_general",
            topic="concept",
            ontological_object_type="entity",
            representation_type="linguistic",
            semantic_type="linguistic",
            relation_type="linguistic",
            inference_type="deductive",
            judgment_basis_type="semantic",
        )
    )
    assert decision.status == "invalid_measure"
    assert decision.gates["semantic_inference_gate"] is False
    assert decision.gates["semantic_layer_separation_gate"] is False
    assert "dalala_without_gate" in decision.residuals
    assert "invalid_semantic_transition" in decision.residuals
