from __future__ import annotations

from types import SimpleNamespace

from mcd.governance import (
    from_cfk_proof,
    to_unified_kernel_from_cfk_proof,
    to_unified_kernel_from_concept_claim,
)
from mcd.nabhani.concept_claim_governance_evaluator import ConceptClaim, ConceptClaimGovernanceEvaluator


def test_unified_kernel_adapter_keeps_legacy_canonical_adapter_unchanged():
    proof = SimpleNamespace(
        judgment="hypothesis",
        proof_id="PO-77",
        conservation=SimpleNamespace(passed=True),
        reverse_trace_obj=SimpleNamespace(reverse_trace_id="RT-77", blocking_violations=[]),
        residual_type="none",
        residuals=["certificate_blocked"],
    )
    canonical = from_cfk_proof(proof).to_dict()
    assert set(canonical.keys()) == {
        "runtime",
        "judgment",
        "proof_object_ref",
        "governance_gate_passed",
        "reverse_trace_ref",
        "trace_graph_ref",
        "legitimacy_state",
        "rank_calculus_state",
        "residuals",
    }


def test_unified_kernel_adapter_maps_cfk_record_without_field_redefinition():
    proof = SimpleNamespace(
        judgment="hypothesis",
        proof_id="PO-88",
        conservation=SimpleNamespace(passed=True),
        reverse_trace_obj=SimpleNamespace(reverse_trace_id="RT-88", blocking_violations=[]),
        residual_type="none",
        residuals=["reverse_trace_missing"],
    )
    kernel = to_unified_kernel_from_cfk_proof(proof).to_dict()
    assert set(kernel.keys()) == {"Input", "Candidates", "Constraints", "Evidence", "Residuals", "Decision", "Trace"}
    assert kernel["Trace"]["proof_object_ref"] == "PO-88"
    assert kernel["Trace"]["reverse_trace_ref"] == "RT-88"


def test_unified_kernel_adapter_maps_concept_claim_flow():
    evaluator = ConceptClaimGovernanceEvaluator()
    claim = ConceptClaim(
        claim="Water boils at 100C under standard pressure.",
        domain="scientific_experimental",
        topic="material",
        thinking_type="deep",
        reality_anchor="lab observation",
        sensation_path="experiment",
        prior_information=["boiling point basics"],
        governing_measure="experimental",
        certainty_level="HYPOTHESIS",
        evidence_refs=["exp-001"],
        reverse_trace_ref="rt-100",
    )
    decision = evaluator.evaluate(claim)
    kernel = to_unified_kernel_from_concept_claim(claim, decision).to_dict()
    assert kernel["Input"]["domain"] == "scientific_experimental"
    assert kernel["Input"]["topic"] == "material"
    assert kernel["Input"]["ontological_object_type"] == ""
    assert kernel["Input"]["representation_type"] == ""
    assert kernel["Decision"]["status"] == "accepted"
    assert kernel["Trace"]["reverse_trace_complete"] is True
