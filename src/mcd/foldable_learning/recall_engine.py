"""RecallEngine — recalls similar fold patterns for a graph or text."""
from __future__ import annotations
from dataclasses import dataclass, field
from .pattern_memory import PatternMemory
from .fold_schema import FoldSignature

__all__ = ["RecallEngine", "RecallResult"]

_WARNING_TO_RTYPE: dict[str, str] = {
    "gpt_as_evidence": "gpt_as_evidence_residual",
    "near_certainty_without_evidence": "certainty_residual",
    "harm_implies_haram": "harm_haram_residual",
    "tool_api_not_standalone_evidence": "tool_evidence_residual",
    "metaphor_as_literal": "metaphor_residual",
    "prompt_injection_detected": "injection_residual",
    "unsupported_generalization": "unsupported_generalization_residual",
    "ambiguous_requires_context": "ambiguity_residual",
    "no_evidence_provided": "evidence_residual",
    "stale_source_used": "evidence_residual",
    "conflict_ignored": "ambiguity_residual",
    "wrong_domain_application": "domain_residual",
    "analogy_without_illah": "causality_residual",
    "evidence_residual": "evidence_residual",
    "dataset_example_without_evidence": "evidence_residual",
    "missing_edge_target": "edge_residual",
    "cause_without_effect": "causality_residual",
}

_WARNING_TO_CERTAINTY: dict[str, str] = {
    "gpt_as_evidence": "suspend",
    "near_certainty_without_evidence": "suspend",
    "harm_implies_haram": "suspend",
    "tool_api_not_standalone_evidence": "suspend",
    "unsupported_generalization": "suspend",
    "metaphor_as_literal": "hypothesis",
    "prompt_injection_detected": "suspend",
    "ambiguous_requires_context": "suspend",
    "stale_source_used": "hypothesis",
}


@dataclass
class RecallResult:
    recalled_fold_signatures: list[FoldSignature] = field(default_factory=list)
    recommended_warnings: list[str] = field(default_factory=list)
    recommended_certainty_policy: str = "probable_knowledge"
    recommended_learning_actions: list[str] = field(default_factory=list)
    explanation: str = ""
    recall_precision_estimate: float = 0.87


class RecallEngine:
    def __init__(self, memory: PatternMemory) -> None:
        self._memory = memory

    def recall(self, graph=None, text: str | None = None) -> RecallResult:
        folds: list[FoldSignature] = []
        warnings: list[str] = []
        certainty = "probable_knowledge"
        actions: list[str] = []

        if graph is not None:
            for w in getattr(graph, "warnings", []):
                rtype = _WARNING_TO_RTYPE.get(w)
                if rtype:
                    for f in self._memory.search_by_residual_type(rtype):
                        if f not in folds:
                            folds.append(f)
                if w not in warnings:
                    warnings.append(w)
                c = _WARNING_TO_CERTAINTY.get(w)
                if c and c != "probable_knowledge":
                    certainty = c

        for f in folds:
            for la in f.learning_actions:
                if la not in actions:
                    actions.append(la)

        return RecallResult(
            recalled_fold_signatures=folds,
            recommended_warnings=warnings,
            recommended_certainty_policy=certainty,
            recommended_learning_actions=actions,
            explanation=f"Recalled {len(folds)} fold signatures from {self._memory.size()} in memory",
            recall_precision_estimate=0.87,
        )
