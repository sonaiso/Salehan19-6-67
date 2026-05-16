"""Adapters that canonicalize governance outputs across runtimes."""
from __future__ import annotations

from mcd.core.public_judgment import collapse_to_public_judgment, enforce_governed_output_contract
from mcd.governance.contracts import CanonicalGovernanceRecord
from mcd.governance.unified_kernel import UnifiedGovernanceKernel, from_canonical_record


def from_cfk_proof(proof) -> CanonicalGovernanceRecord:
    rt_obj = getattr(proof, "reverse_trace_obj", None)
    conservation = getattr(proof, "conservation", None)
    conservation_passed = bool(getattr(conservation, "passed", False))
    blocking = bool(getattr(rt_obj, "blocking_violations", []))
    governance_gate_passed = conservation_passed and not blocking
    residuals = list(getattr(proof, "residuals", []) or [])
    residual_type = getattr(proof, "residual_type", "none")
    if residual_type not in {"", "none"}:
        residuals.append(residual_type)
    payload = enforce_governed_output_contract(
        {
            "runtime": "cfk",
            "judgment": collapse_to_public_judgment(getattr(proof, "judgment", "")),
            "proof_object_ref": getattr(proof, "proof_id", ""),
            "governance_gate_passed": governance_gate_passed,
            "reverse_trace_ref": getattr(rt_obj, "reverse_trace_id", ""),
            "trace_graph_ref": "TraceGraph.canonical",
            "legitimacy_state": "legitimate" if governance_gate_passed else "blocked",
            "rank_calculus_state": collapse_to_public_judgment(getattr(proof, "judgment", "")),
            "residuals": list(dict.fromkeys(r for r in residuals if r)),
        }
    )
    return CanonicalGovernanceRecord(
        runtime=payload["runtime"],
        judgment=payload["judgment"],
        proof_object_ref=payload["proof_object_ref"],
        governance_gate_passed=payload["governance_gate_passed"],
        reverse_trace_ref=payload["reverse_trace_ref"],
        trace_graph_ref=payload["trace_graph_ref"],
        legitimacy_state=payload["legitimacy_state"],
        rank_calculus_state=payload["rank_calculus_state"],
        residuals=payload["residuals"],
    )


def from_fractal_kernel_proof(proof) -> CanonicalGovernanceRecord:
    blockers = list(getattr(proof, "blockers", []))
    governance_gate_passed = getattr(proof, "proof_status", "") == "certificate" and not blockers
    payload = enforce_governed_output_contract(
        {
            "runtime": "fractal_kernel",
            "judgment": collapse_to_public_judgment(getattr(proof, "proof_status", "")),
            "proof_object_ref": getattr(proof, "proof_id", ""),
            "governance_gate_passed": governance_gate_passed,
            "reverse_trace_ref": getattr(proof, "reverse_trace_id", "") or "",
            "trace_graph_ref": "TraceGraph.canonical",
            "legitimacy_state": "legitimate" if governance_gate_passed else "blocked",
            "rank_calculus_state": collapse_to_public_judgment(getattr(proof, "proof_status", "")),
            "residuals": blockers,
        }
    )
    return CanonicalGovernanceRecord(
        runtime=payload["runtime"],
        judgment=payload["judgment"],
        proof_object_ref=payload["proof_object_ref"],
        governance_gate_passed=payload["governance_gate_passed"],
        reverse_trace_ref=payload["reverse_trace_ref"],
        trace_graph_ref=payload["trace_graph_ref"],
        legitimacy_state=payload["legitimacy_state"],
        rank_calculus_state=payload["rank_calculus_state"],
        residuals=payload["residuals"],
    )


def from_coding_judgment(judgment) -> CanonicalGovernanceRecord:
    trace = getattr(judgment, "reverse_trace", None)
    trace_complete = bool(getattr(trace, "complete", False))
    residuals = [getattr(r, "residual_type", "") for r in getattr(judgment, "residuals", [])]
    governance_gate_passed = (
        collapse_to_public_judgment(getattr(judgment, "final_judgment", "")) == "certificate"
        and trace_complete
    )
    payload = enforce_governed_output_contract(
        {
            "runtime": "coding_copilot",
            "judgment": collapse_to_public_judgment(getattr(judgment, "final_judgment", "")),
            "proof_object_ref": getattr(judgment, "judgment_id", ""),
            "governance_gate_passed": governance_gate_passed,
            "reverse_trace_ref": getattr(trace, "trace_id", "") if trace else "",
            "trace_graph_ref": "TraceGraph.canonical",
            "legitimacy_state": "legitimate" if governance_gate_passed else "blocked",
            "rank_calculus_state": collapse_to_public_judgment(getattr(judgment, "final_judgment", "")),
            "residuals": [r for r in residuals if r],
        }
    )
    return CanonicalGovernanceRecord(
        runtime=payload["runtime"],
        judgment=payload["judgment"],
        proof_object_ref=payload["proof_object_ref"],
        governance_gate_passed=payload["governance_gate_passed"],
        reverse_trace_ref=payload["reverse_trace_ref"],
        trace_graph_ref=payload["trace_graph_ref"],
        legitimacy_state=payload["legitimacy_state"],
        rank_calculus_state=payload["rank_calculus_state"],
        residuals=payload["residuals"],
    )


def to_unified_kernel_from_cfk_proof(proof) -> UnifiedGovernanceKernel:
    return from_canonical_record(from_cfk_proof(proof))


def to_unified_kernel_from_fractal_kernel_proof(proof) -> UnifiedGovernanceKernel:
    return from_canonical_record(from_fractal_kernel_proof(proof))


def to_unified_kernel_from_coding_judgment(judgment) -> UnifiedGovernanceKernel:
    return from_canonical_record(from_coding_judgment(judgment))


def to_unified_kernel_from_concept_claim(claim, decision) -> UnifiedGovernanceKernel:
    certificate_requested = str(getattr(claim, "certainty_level", "")).strip().lower() == "certificate"
    gates = dict(getattr(decision, "gates", {}) or {})
    reverse_trace_ref = getattr(claim, "reverse_trace_ref", None)
    constraints = [{"id": gate_name, "passed": bool(gate_result)} for gate_name, gate_result in gates.items()]
    evidence = [{"type": "evidence_ref", "ref": ref} for ref in list(getattr(claim, "evidence_refs", []) or []) if str(ref).strip()]
    return UnifiedGovernanceKernel(
        Input={
            "claim": getattr(claim, "claim", ""),
            "domain": getattr(claim, "domain", ""),
            "topic": getattr(claim, "topic", ""),
            "thinking_type": getattr(claim, "thinking_type", ""),
            "governing_measure": getattr(claim, "governing_measure", ""),
            "ontological_object_type": getattr(claim, "ontological_object_type", "") or "",
            "representation_type": getattr(claim, "representation_type", "") or "",
            "relation_type": getattr(claim, "relation_type", "") or "",
            "semantic_type": getattr(claim, "semantic_type", "") or "",
            "inference_type": getattr(claim, "inference_type", "") or "",
        },
        Candidates=[{"certainty_level": getattr(claim, "certainty_level", ""), "status": getattr(decision, "status", "")}],
        Constraints=constraints,
        Evidence=evidence,
        Residuals=list(getattr(decision, "residuals", []) or []),
        Decision={
            "status": getattr(decision, "status", ""),
            "certainty_level": getattr(decision, "certainty_level", ""),
            "certificate_requested": certificate_requested,
            "certificate_allowed": bool(getattr(decision, "can_issue_certificate", False)),
        },
        Trace={
            "reverse_trace_ref": reverse_trace_ref or "",
            "reverse_trace_complete": bool(reverse_trace_ref),
        },
    )
