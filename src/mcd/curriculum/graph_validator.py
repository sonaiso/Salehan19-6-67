"""GraphValidator — validates structural integrity of a CognitiveGraph."""
from __future__ import annotations

from dataclasses import dataclass, field

from .cognitive_graph import CognitiveGraph
from .cognitive_node import NODE_TYPES
from .cognitive_edge import VALID_RELATIONS


@dataclass
class GraphValidationResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 1.0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": self.violations,
            "warnings": self.warnings,
            "score": round(self.score, 4),
        }


def validate_graph(graph: CognitiveGraph) -> GraphValidationResult:
    violations: list[str] = []
    warnings: list[str] = []

    # Must have nodes
    if not graph.nodes:
        violations.append("graph has no nodes (INV-001)")

    # Must have root_vector
    if not graph.root_vector:
        violations.append("graph has no root_vector")

    node_ids = graph.node_ids()

    # Validate each node
    for node in graph.nodes:
        if node.node_type not in NODE_TYPES:
            violations.append(f"node '{node.node_id}' has invalid node_type '{node.node_type}'")

    # Validate edges: all endpoints must exist
    for edge in graph.edges:
        if edge.source not in node_ids:
            violations.append(f"edge '{edge.edge_id}' source '{edge.source}' not in graph nodes (INV-002)")
        if edge.target not in node_ids:
            violations.append(f"edge '{edge.edge_id}' target '{edge.target}' not in graph nodes (INV-002)")
        if edge.relation not in VALID_RELATIONS:
            violations.append(f"edge '{edge.edge_id}' has invalid relation '{edge.relation}'")

    # Cause edges must have corresponding effect
    cause_targets = {e.target for e in graph.edges if e.relation == "causes"}
    effect_nodes = {n.node_id for n in graph.nodes if n.node_type == "effect"}
    for ct in cause_targets:
        # We only warn if the target is not an effect node
        if ct not in effect_nodes:
            warnings.append(f"cause target '{ct}' is not typed as effect node (INV-003)")

    # near_certainty requires evidence
    if graph.certainty_policy == "near_certainty":
        has_evidence = any(
            n.node_type in ("evidence", "source") and n.evidence_refs
            for n in graph.nodes
        )
        if not has_evidence:
            violations.append("near_certainty policy requires evidence_refs (INV-004)")

    # source_required warning prevents near_certainty
    if "source_required" in graph.warnings and graph.certainty_policy == "near_certainty":
        violations.append("certainty_policy near_certainty blocked by source_required warning (INV-004)")

    # evidence_status sufficient requires actual evidence
    if graph.evidence_status == "sufficient":
        all_evidence_empty = all(
            not n.evidence_refs
            for n in graph.nodes
            if n.node_type in ("evidence", "source")
        )
        if all_evidence_empty:
            violations.append("evidence_status 'sufficient' but all evidence nodes have empty evidence_refs")

    # JSON serializable check
    if not graph.is_json_serializable():
        violations.append("graph is not JSON serializable (INV-010)")

    passed = len(violations) == 0
    score = max(0.0, 1.0 - 0.1 * len(violations) - 0.02 * len(warnings))
    return GraphValidationResult(passed=passed, violations=violations, warnings=warnings, score=score)
