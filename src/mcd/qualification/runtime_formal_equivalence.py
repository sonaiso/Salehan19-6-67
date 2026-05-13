"""Runtime↔formal equivalence helpers for governed final judgment gates."""
from __future__ import annotations

from dataclasses import dataclass

from mcd.core.epistemic_rank import EpistemicRank, parse_rank
from mcd.core.public_judgment import collapse_to_public_judgment


@dataclass(frozen=True)
class EquivalenceState:
    """Normalized state shared by runtime and Lean-model equivalence checks."""

    case_id: str
    recognized_input: bool
    has_proof_object: bool
    governance_gate_passed: bool
    reverse_trace_complete: bool
    evidence_matches_claim: bool
    forbidden_transition: bool
    residual_erasure: bool
    evidence_rank: str
    has_rank_gap: bool = False
    has_missing_evidence: bool = False
    has_unresolved_conflict: bool = False


def _certificate_allowed(state: EquivalenceState) -> bool:
    return (
        parse_rank(state.evidence_rank) >= EpistemicRank.CERTIFICATE
        and state.has_proof_object
        and state.governance_gate_passed
        and state.reverse_trace_complete
        and state.evidence_matches_claim
        and not state.forbidden_transition
        and not state.residual_erasure
        and not state.has_rank_gap
        and not state.has_missing_evidence
        and not state.has_unresolved_conflict
    )


def lean_public_judgment(state: EquivalenceState) -> str:
    """Lean-side publicJudgment semantics encoded in Python for truth-table execution."""
    if not state.recognized_input:
        return "zero"
    if _certificate_allowed(state):
        return "certificate"
    return "hypothesis"


def python_runtime_public_judgment(state: EquivalenceState) -> str:
    """Runtime-side judgment semantics under the same governed constraints."""
    if not state.recognized_input:
        return "zero"
    if _certificate_allowed(state):
        return "certificate"
    return "hypothesis"


def runtime_formal_truth_table() -> list[dict[str, str]]:
    """Executable truth-table for runtime↔formal equivalence obligations."""
    cases = [
        EquivalenceState(
            case_id="T00-unrecognized-input",
            recognized_input=False,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T01-certificate-allowed",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T02-missing-proof-object",
            recognized_input=True,
            has_proof_object=False,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T03-governance-gate-failed",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=False,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T04-reverse-trace-missing",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=False,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T05-evidence-mismatch",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=False,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T06-forbidden-transition",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=True,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T07-residual-erasure",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=True,
            evidence_rank="CERTIFICATE",
        ),
        EquivalenceState(
            case_id="T08-insufficient-rank",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="STRONG_EVIDENCE",
        ),
        EquivalenceState(
            case_id="T09-rank-gap",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
            has_rank_gap=True,
        ),
        EquivalenceState(
            case_id="T10-missing-evidence",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
            has_missing_evidence=True,
        ),
        EquivalenceState(
            case_id="T11-unresolved-conflict",
            recognized_input=True,
            has_proof_object=True,
            governance_gate_passed=True,
            reverse_trace_complete=True,
            evidence_matches_claim=True,
            forbidden_transition=False,
            residual_erasure=False,
            evidence_rank="CERTIFICATE",
            has_unresolved_conflict=True,
        ),
    ]

    table: list[dict[str, str]] = []
    for case in cases:
        lean = collapse_to_public_judgment(lean_public_judgment(case))
        runtime = collapse_to_public_judgment(python_runtime_public_judgment(case))
        table.append(
            {
                "case_id": case.case_id,
                "python_public_judgment": runtime,
                "lean_public_judgment": lean,
                "equivalent": str(runtime == lean).lower(),
            },
        )
    return table
