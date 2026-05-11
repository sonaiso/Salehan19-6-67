from __future__ import annotations

from .dimension import EpistemicDimension
from .edge import MinimalFractalEdge
from .folding import FoldedNodeSummary, RetrievalPath
from .node import MinimalFractalNode


def validate_gate_score_separation(
    node: MinimalFractalNode,
    dimensions: list[EpistemicDimension] | None = None,
) -> list[str]:
    violations: list[str] = []
    for gate_name, gate_value in node.gates.items():
        if gate_value not in (0, 1):
            violations.append(f"gate_not_boolean:{gate_name}")
    for score_name, score_value in node.scores.items():
        if not (0.0 <= score_value <= 1.0):
            violations.append(f"score_out_of_range:{score_name}")
    for key, gate_value in node.gates.items():
        score_value = node.scores.get(key)
        if gate_value == 0 and score_value is not None and score_value > 0.0:
            violations.append(f"score_cannot_open_gate:{key}")
    for dim in dimensions or []:
        if dim.gate == 0 and dim.score > 0.0:
            violations.append(f"score_cannot_open_gate:{dim.dimension_id}")
    return violations


def validate_node_minimum_completeness(node: MinimalFractalNode) -> list[str]:
    violations: list[str] = []
    if not node.gates:
        violations.append("node_requires_gate")
    if not node.trace_refs:
        violations.append("node_requires_trace_refs")
    if not node.domain and "domain_missing" not in node.residuals:
        violations.append("node_requires_domain_or_domain_missing_residual")
    if node.judgment == "CERTIFICATE":
        violations.append("no_certificate_from_node_alone")
    return violations


def validate_edge_morphism(edge: MinimalFractalEdge) -> list[str]:
    violations: list[str] = []
    if not edge.morphism_id:
        violations.append("edge_requires_morphism")
    if not edge.relation_type:
        violations.append("edge_requires_relation_type")
    if edge.residual_policy.get("erase") == "silent":
        violations.append("edge_cannot_erase_residual")
    return violations


def validate_no_silent_skip(edge: MinimalFractalEdge) -> list[str]:
    if edge.level_step > 1:
        return ["no_silent_level_skip"]
    return []


def validate_folding_preserves_residuals(
    node: MinimalFractalNode,
    summary: FoldedNodeSummary,
) -> list[str]:
    if not set(node.residuals).issubset(set(summary.blocking_residuals)):
        return ["folding_must_preserve_residuals"]
    return []


def validate_retrieval_has_trace(path: RetrievalPath) -> list[str]:
    if not path.reverse_trace:
        return ["retrieval_requires_trace"]
    return []

