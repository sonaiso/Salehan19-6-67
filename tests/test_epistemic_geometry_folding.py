from mcd.epistemic_geometry import MinimalFractalNode, RetrievalPath, fold_node
from mcd.epistemic_geometry.validators import (
    validate_folding_preserves_residuals,
    validate_retrieval_has_trace,
)


def _base_node(**kwargs) -> MinimalFractalNode:
    defaults = dict(
        node_id="node-fold-1",
        rank=2,
        node_type="evidence",
        domain="factual",
        gates={"trace": 1, "evidence": 1},
        scores={"trace": 1.0, "evidence": 0.9},
        trace_refs=["trace-1"],
        residuals=["domain_scope_partial"],
        relations=[{"type": "evidence"}],
        incoming_edges=["edge-in-1"],
        outgoing_edges=["edge-out-1"],
        allowed_next=["judgment"],
        forbidden_transitions=["silent_level_skip"],
    )
    defaults.update(kwargs)
    return MinimalFractalNode(**defaults)


def test_folding_preserves_blocking_residual():
    node = _base_node()
    summary = fold_node(node)
    assert validate_folding_preserves_residuals(node, summary) == []
    assert "domain_scope_partial" in summary.blocking_residuals


def test_retrieval_reconstructs_trace():
    path = RetrievalPath(
        folded_node_id="node-fold-1",
        expanded_dimensions=["trace", "evidence"],
        expanded_edges=["edge-in-1", "edge-out-1"],
        residual_path=["domain_scope_partial"],
        reverse_trace=["trace-1"],
    )
    assert validate_retrieval_has_trace(path) == []

