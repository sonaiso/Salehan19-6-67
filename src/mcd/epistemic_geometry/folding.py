from __future__ import annotations

from dataclasses import dataclass, field

from .node import MinimalFractalNode


@dataclass
class FoldedNodeSummary:
    node_id: str
    passed_gates_count: int
    failed_critical_gates: list[str] = field(default_factory=list)
    completeness_score: float = 0.0
    domain: str = ""
    relation_count: int = 0
    blocking_residuals: list[str] = field(default_factory=list)
    trace_status: str = "missing"
    judgment_boundary: str = "HYPOTHESIS"


@dataclass
class RetrievalPath:
    folded_node_id: str
    expanded_dimensions: list[str] = field(default_factory=list)
    expanded_edges: list[str] = field(default_factory=list)
    residual_path: list[str] = field(default_factory=list)
    reverse_trace: list[str] = field(default_factory=list)


def fold_node(node: MinimalFractalNode) -> FoldedNodeSummary:
    gate_values = list(node.gates.values())
    passed = sum(1 for value in gate_values if value == 1)
    failed = [key for key, value in node.gates.items() if value == 0]
    score_values = list(node.scores.values())
    completeness = (sum(score_values) / len(score_values)) if score_values else 0.0
    trace_status = "present" if node.trace_refs else "missing"
    return FoldedNodeSummary(
        node_id=node.node_id,
        passed_gates_count=passed,
        failed_critical_gates=failed,
        completeness_score=completeness,
        domain=node.domain,
        relation_count=len(node.relations),
        blocking_residuals=list(node.residuals),
        trace_status=trace_status,
        judgment_boundary=node.judgment,
    )

