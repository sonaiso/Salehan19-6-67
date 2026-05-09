"""ResidualCalculator — computes CognitiveResidual from a GPTProposal.

Formula:  CognitiveResidual = GPTProposal − MathematicalContract

The calculator maps contract violations and parser warnings to typed residuals.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .proposal_schema import GPTProposal, ProposalGraph
from .residual_schema import CognitiveResidual, ResidualType, Severity


# ── Violation → residual type mapping ──────────────────────────────────────

_VIOLATION_MAP: dict[str, list[str]] = {
    # Contract rule 7: near_certainty without evidence
    "Contract[7]": [ResidualType.CERTAINTY.value, ResidualType.EVIDENCE.value],
    # Contract rule 9: harm ≠ haram
    "Contract[9]": [ResidualType.HARM_HARAM.value],
    # Contract rule 10: tool/API not standalone evidence
    "Contract[10]": [ResidualType.TOOL_EVIDENCE.value],
    # Contract rule 4: missing edge endpoint
    "Contract[4]": [ResidualType.EDGE.value],
    # Contract rule 5: cause without effect
    "Contract[5]": [ResidualType.CAUSALITY.value],
    # Contract rule 1: no nodes
    "Contract[1]": [ResidualType.STRUCTURAL.value],
    # Contract rule 2/3: missing / invalid vectors
    "Contract[2]": [ResidualType.VECTOR.value],
    "Contract[3]": [ResidualType.VECTOR.value],
    # Contract rule 8: ambiguous → near_certainty conflict
    "Contract[8]": [ResidualType.AMBIGUITY.value, ResidualType.CERTAINTY.value],
}

# Proposal-graph warning → residual type mapping
_WARNING_MAP: dict[str, list[str]] = {
    "near_certainty_without_evidence": [ResidualType.CERTAINTY.value, ResidualType.EVIDENCE.value],
    "harm_implies_haram": [ResidualType.HARM_HARAM.value],
    "tool_api_not_standalone_evidence": [ResidualType.TOOL_EVIDENCE.value],
    "metaphor_as_literal": [ResidualType.METAPHOR.value],
    "prompt_injection_detected": [ResidualType.INJECTION.value],
    "unsupported_generalization": [ResidualType.UNSUPPORTED_GENERALIZATION.value, ResidualType.EVIDENCE.value],
    "ambiguous_requires_context": [ResidualType.AMBIGUITY.value],
    "no_evidence_provided": [ResidualType.EVIDENCE.value],
    "dataset_example_without_evidence": [ResidualType.EVIDENCE.value],
    "missing_edge_target": [ResidualType.EDGE.value],
    "cause_without_effect": [ResidualType.CAUSALITY.value],
}

# Residual-type → severity mapping (worst-case rule)
_TYPE_SEVERITY: dict[str, str] = {
    ResidualType.HARM_HARAM.value: Severity.BLOCKING.value,
    ResidualType.INJECTION.value: Severity.BLOCKING.value,
    ResidualType.TOOL_EVIDENCE.value: Severity.HIGH.value,
    ResidualType.CERTAINTY.value: Severity.HIGH.value,
    ResidualType.EVIDENCE.value: Severity.HIGH.value,
    ResidualType.UNSUPPORTED_GENERALIZATION.value: Severity.HIGH.value,
    ResidualType.CAUSALITY.value: Severity.MEDIUM.value,
    ResidualType.METAPHOR.value: Severity.MEDIUM.value,
    ResidualType.AMBIGUITY.value: Severity.MEDIUM.value,
    ResidualType.EDGE.value: Severity.MEDIUM.value,
    ResidualType.VECTOR.value: Severity.LOW.value,
    ResidualType.STRUCTURAL.value: Severity.LOW.value,
    ResidualType.DOMAIN.value: Severity.LOW.value,
}

_SEVERITY_ORDER = [Severity.LOW.value, Severity.MEDIUM.value, Severity.HIGH.value, Severity.BLOCKING.value]


def _max_severity(types: list[str]) -> str:
    best = Severity.LOW.value
    for t in types:
        s = _TYPE_SEVERITY.get(t, Severity.LOW.value)
        if _SEVERITY_ORDER.index(s) > _SEVERITY_ORDER.index(best):
            best = s
    return best


@dataclass
class MathematicalContractResult:
    """Minimal local version — accepts the real MCR from curriculum package too."""
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 1.0

    @classmethod
    def from_dict(cls, d: dict) -> "MathematicalContractResult":
        return cls(
            passed=d.get("passed", True),
            violations=d.get("violations", []),
            warnings=d.get("warnings", []),
            score=d.get("score", 1.0),
        )


class ResidualCalculator:
    """Calculates CognitiveResidual from (GPTProposal, ProposalGraph, ContractResult).

    GPT output is NEVER used as evidence.
    GPT output cannot increase certainty.
    """

    def calculate(
        self,
        proposal: GPTProposal,
        proposal_graph: ProposalGraph,
        contract_result: MathematicalContractResult | None = None,
    ) -> CognitiveResidual:
        residual_types: list[str] = []
        evidence_gaps: list[str] = []
        certainty_errors: list[str] = []
        causality_errors: list[str] = []
        metaphor_errors: list[str] = []
        safety_errors: list[str] = []
        invariant_violations: list[str] = []
        missing_nodes: list[str] = []
        missing_edges: list[str] = []
        invalid_edges: list[str] = []
        vector_deviations: dict[str, float] = {}
        explanations: list[str] = []

        # ── 1. Map contract violations ──────────────────────────────────────
        if contract_result:
            for violation in contract_result.violations:
                for prefix, types in _VIOLATION_MAP.items():
                    if violation.startswith(prefix):
                        for t in types:
                            if t not in residual_types:
                                residual_types.append(t)
                        if prefix == "Contract[7]":
                            certainty_errors.append(violation)
                            evidence_gaps.append(violation)
                        elif prefix == "Contract[5]":
                            causality_errors.append(violation)
                        elif prefix in ("Contract[4]",):
                            missing_edges.append(violation)
                        elif prefix in ("Contract[1]", "Contract[2]", "Contract[3]"):
                            missing_nodes.append(violation)
                        break

            for warning in contract_result.warnings:
                for prefix, types in _VIOLATION_MAP.items():
                    if warning.startswith(prefix):
                        for t in types:
                            if t not in residual_types:
                                residual_types.append(t)
                        break

        # ── 2. Map proposal-graph warnings ─────────────────────────────────
        for w in proposal_graph.warnings:
            types = _WARNING_MAP.get(w, [])
            for t in types:
                if t not in residual_types:
                    residual_types.append(t)
            # Route to specific error buckets
            if w == "near_certainty_without_evidence":
                certainty_errors.append("near_certainty_without_evidence")
                evidence_gaps.append("no_evidence_in_proposal")
            elif w == "harm_implies_haram":
                safety_errors.append("harm_implies_haram")
                invariant_violations.append("harm_haram_invariant")
            elif w == "tool_api_not_standalone_evidence":
                evidence_gaps.append("tool_api_as_evidence_rejected")
            elif w == "metaphor_as_literal":
                metaphor_errors.append("metaphor_treated_as_literal")
            elif w == "prompt_injection_detected":
                safety_errors.append("prompt_injection_followed")
            elif w == "unsupported_generalization":
                evidence_gaps.append("unsupported_generalization_no_source")
            elif w == "ambiguous_requires_context":
                explanations.append("ambiguous input requires context before judgment")
            elif w == "no_evidence_provided":
                evidence_gaps.append("proposal_has_no_evidence")

        # ── 3. GPT output is never evidence ────────────────────────────────
        # If the proposal claims GPT output itself as evidence, that's a residual.
        gpt_as_evidence_markers = ["gpt", "chatgpt", "النموذج", "الذكاء الاصطناعي"]
        for e in proposal.claimed_evidence:
            if any(m in e.lower() for m in gpt_as_evidence_markers):
                if ResidualType.TOOL_EVIDENCE.value not in residual_types:
                    residual_types.append(ResidualType.TOOL_EVIDENCE.value)
                evidence_gaps.append(f"gpt_output_as_evidence_rejected: {e}")

        # ── 4. GPT output cannot increase certainty ─────────────────────────
        high_certainty = proposal.claimed_certainty in ("certain", "definite", "يقين", "قطعي")
        if high_certainty and not proposal.claimed_evidence:
            if ResidualType.CERTAINTY.value not in residual_types:
                residual_types.append(ResidualType.CERTAINTY.value)
            if ResidualType.EVIDENCE.value not in residual_types:
                residual_types.append(ResidualType.EVIDENCE.value)
            certainty_errors.append("false_certainty_without_evidence")

        # ── 5. Vector deviations from proposal graph ───────────────────────
        for key, val in proposal_graph.root_vector.items():
            if key in ("tool_as_evidence", "harm_haram_equivocation", "injection_risk",
                       "metaphor_literalization", "generalization_without_evidence"):
                if val > 0.5:
                    vector_deviations[key] = val

        # ── 6. Calculate residual score ─────────────────────────────────────
        score = 0.0
        score += len(residual_types) * 0.1
        score += len(evidence_gaps) * 0.08
        score += len(certainty_errors) * 0.1
        score += len(safety_errors) * 0.15
        score += len(invariant_violations) * 0.2
        score += sum(vector_deviations.values()) * 0.05
        score = min(1.0, score)

        severity = _max_severity(residual_types) if residual_types else Severity.LOW.value

        explanation_parts = []
        if not residual_types:
            explanation_parts.append("No residuals detected — proposal passed all contract checks.")
        else:
            explanation_parts.append(f"Residual types: {', '.join(residual_types)}.")
        explanation_parts.extend(explanations)

        return CognitiveResidual(
            residual_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            residual_types=residual_types,
            missing_nodes=missing_nodes,
            missing_edges=missing_edges,
            invalid_edges=invalid_edges,
            vector_deviations=vector_deviations,
            evidence_gaps=evidence_gaps,
            certainty_errors=certainty_errors,
            domain_errors=[],
            causality_errors=causality_errors,
            metaphor_errors=metaphor_errors,
            safety_errors=safety_errors,
            invariant_violations=invariant_violations,
            severity=severity,
            residual_score=score,
            explanation=" ".join(explanation_parts),
        )
