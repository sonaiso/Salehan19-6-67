"""Phase 2.1D — Minimal complete fractal epistemic geometry contracts."""
from .dimension import DIMENSION_TYPES, EpistemicDimension
from .edge import MinimalFractalEdge
from .folding import FoldedNodeSummary, RetrievalPath, fold_node
from .node import FINAL_JUDGMENTS, MinimalFractalNode
from .validators import (
    validate_edge_morphism,
    validate_folding_preserves_residuals,
    validate_gate_score_separation,
    validate_no_silent_skip,
    validate_node_minimum_completeness,
    validate_retrieval_has_trace,
)

__all__ = [
    "DIMENSION_TYPES",
    "FINAL_JUDGMENTS",
    "EpistemicDimension",
    "MinimalFractalEdge",
    "MinimalFractalNode",
    "FoldedNodeSummary",
    "RetrievalPath",
    "fold_node",
    "validate_gate_score_separation",
    "validate_node_minimum_completeness",
    "validate_edge_morphism",
    "validate_no_silent_skip",
    "validate_folding_preserves_residuals",
    "validate_retrieval_has_trace",
]
