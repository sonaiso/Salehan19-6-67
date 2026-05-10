"""Foldable ResidualCalculator — extends base with gpt_as_evidence and extra warnings."""
from __future__ import annotations
from mcd.residual_learning.residual_calculator import ResidualCalculator as _BaseCalc
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalGraph
from mcd.residual_learning.residual_schema import CognitiveResidual, Severity

__all__ = ["ResidualCalculator"]

_FOLDABLE_WARNING_MAP: dict[str, list[str]] = {
    "gpt_as_evidence": ["gpt_as_evidence_residual", "evidence_residual"],
    "stale_source_used": ["evidence_residual", "traceability_residual"],
    "conflict_ignored": ["ambiguity_residual"],
    "wrong_domain_application": ["domain_residual"],
    "analogy_without_illah": ["causality_residual"],
    "evidence_residual": ["evidence_residual"],
}

_FOLDABLE_SEVERITY_MAP = {
    "gpt_as_evidence_residual": Severity.BLOCKING.value,
    "traceability_residual": Severity.HIGH.value,
    "domain_residual": Severity.MEDIUM.value,
}

_SEVERITY_ORDER = ["low", "medium", "high", "blocking"]


class ResidualCalculator:
    def __init__(self) -> None:
        self._base = _BaseCalc()

    def calculate(self, proposal: GPTProposal, graph: ProposalGraph) -> CognitiveResidual:
        residual = self._base.calculate(proposal, graph, None)

        for warning in graph.warnings:
            for rt in _FOLDABLE_WARNING_MAP.get(warning, []):
                if rt not in residual.residual_types:
                    residual.residual_types.append(rt)

            # Track gpt_output_used_as_evidence in evidence_gaps
            if warning == "gpt_as_evidence":
                if "gpt_output_used_as_evidence" not in residual.evidence_gaps:
                    residual.evidence_gaps.append("gpt_output_used_as_evidence")

            # Escalate severity
            for rt in _FOLDABLE_WARNING_MAP.get(warning, []):
                new_sev = _FOLDABLE_SEVERITY_MAP.get(rt)
                if new_sev and _SEVERITY_ORDER.index(new_sev) > _SEVERITY_ORDER.index(residual.severity):
                    residual.severity = new_sev

        return residual
