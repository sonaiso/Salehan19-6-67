"""ResidualToFoldConverter — maps CognitiveResidual → FoldSignature."""
from __future__ import annotations
from mcd.residual_learning.residual_schema import CognitiveResidual
from .fold_schema import FoldSignature
from .fold_signature import FoldSignatureRegistry, _RTYPE_TO_FOLDS

__all__ = ["ResidualToFoldConverter"]

# Priority order for picking fold family when multiple match
_PRIORITY = [
    "gpt_as_evidence_residual",
    "harm_haram_residual",
    "injection_residual",
    "tool_evidence_residual",
    "certainty_residual",
    "unsupported_generalization_residual",
    "metaphor_residual",
    "traceability_residual",
    "evidence_residual",
    "ambiguity_residual",
    "causality_residual",
    "domain_residual",
    "structural_residual",
    "vector_residual",
    "edge_residual",
]


def _pick_fold(residual: CognitiveResidual) -> FoldSignature | None:
    for rtype in _PRIORITY:
        if rtype in residual.residual_types:
            folds = FoldSignatureRegistry.find_by_residual_type(rtype)
            if folds:
                return folds[0]
    if residual.residual_types:
        folds = FoldSignatureRegistry.find_by_residual_type(residual.residual_types[0])
        if folds:
            return folds[0]
    return FoldSignatureRegistry.get("FOLD-MISSING-SOURCE")


class ResidualToFoldConverter:
    def convert(self, residual: CognitiveResidual) -> FoldSignature:
        base = _pick_fold(residual)
        if base is None:
            base = FoldSignatureRegistry.get("FOLD-MISSING-SOURCE")
        # Create a copy with residual-specific metadata
        return FoldSignature(
            fold_id=base.fold_id,
            residual_types=list(set(residual.residual_types) | set(base.residual_types)),
            graph_shape=base.graph_shape,
            vector_signature=base.vector_signature.copy(),
            domain_signature=base.domain_signature.copy(),
            evidence_signature=base.evidence_signature,
            certainty_signature=base.certainty_signature,
            trace_signature=base.trace_signature,
            forbidden_confusions=base.forbidden_confusions.copy(),
            recall_keys=base.recall_keys.copy(),
            unfold_plan=base.unfold_plan.copy(),
            learning_actions=base.learning_actions.copy(),
            examples=base.examples.copy(),
            counterexamples=base.counterexamples.copy(),
            metadata={"residual_id": residual.residual_id, "proposal_id": residual.proposal_id},
            severity=residual.severity,
        )

    def batch_convert(self, residuals: list[CognitiveResidual]) -> list[FoldSignature]:
        return [self.convert(r) for r in residuals]
