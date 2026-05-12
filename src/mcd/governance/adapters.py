"""Adapters that canonicalize governance outputs across runtimes."""
from __future__ import annotations

from mcd.core.public_judgment import collapse_to_public_judgment
from mcd.governance.contracts import CanonicalGovernanceRecord


def from_cfk_proof(proof) -> CanonicalGovernanceRecord:
    rt_obj = getattr(proof, "reverse_trace_obj", None)
    conservation = getattr(proof, "conservation", None)
    conservation_passed = bool(getattr(conservation, "passed", False))
    blocking = bool(getattr(rt_obj, "blocking_violations", []))
    governance_gate_passed = conservation_passed and not blocking
    return CanonicalGovernanceRecord(
        runtime="cfk",
        judgment=collapse_to_public_judgment(getattr(proof, "judgment", "")),
        proof_object_ref=getattr(proof, "proof_id", ""),
        governance_gate_passed=governance_gate_passed,
        reverse_trace_ref=getattr(rt_obj, "reverse_trace_id", ""),
        trace_graph_ref="TraceGraph.canonical",
        legitimacy_state="legitimate" if governance_gate_passed else "blocked",
        rank_calculus_state=collapse_to_public_judgment(getattr(proof, "judgment", "")),
        residuals=(
            [getattr(proof, "residual_type", "none")]
            if getattr(proof, "residual_type", "none") not in {"", "none"}
            else []
        ),
    )


def from_fractal_kernel_proof(proof) -> CanonicalGovernanceRecord:
    blockers = list(getattr(proof, "blockers", []))
    governance_gate_passed = getattr(proof, "proof_status", "") == "certificate" and not blockers
    return CanonicalGovernanceRecord(
        runtime="fractal_kernel",
        judgment=collapse_to_public_judgment(getattr(proof, "proof_status", "")),
        proof_object_ref=getattr(proof, "proof_id", ""),
        governance_gate_passed=governance_gate_passed,
        reverse_trace_ref=getattr(proof, "reverse_trace_id", "") or "",
        trace_graph_ref="TraceGraph.canonical",
        legitimacy_state="legitimate" if governance_gate_passed else "blocked",
        rank_calculus_state=collapse_to_public_judgment(getattr(proof, "proof_status", "")),
        residuals=blockers,
    )


def from_coding_judgment(judgment) -> CanonicalGovernanceRecord:
    trace = getattr(judgment, "reverse_trace", None)
    trace_complete = bool(getattr(trace, "complete", False))
    residuals = [getattr(r, "residual_type", "") for r in getattr(judgment, "residuals", [])]
    governance_gate_passed = (
        collapse_to_public_judgment(getattr(judgment, "final_judgment", "")) == "certificate"
        and trace_complete
    )
    return CanonicalGovernanceRecord(
        runtime="coding_copilot",
        judgment=collapse_to_public_judgment(getattr(judgment, "final_judgment", "")),
        proof_object_ref=getattr(judgment, "judgment_id", ""),
        governance_gate_passed=governance_gate_passed,
        reverse_trace_ref=getattr(trace, "trace_id", "") if trace else "",
        trace_graph_ref="TraceGraph.canonical",
        legitimacy_state="legitimate" if governance_gate_passed else "blocked",
        rank_calculus_state=collapse_to_public_judgment(getattr(judgment, "final_judgment", "")),
        residuals=[r for r in residuals if r],
    )
