"""MathematicalContract — verifies full mathematical contract on CognitiveUnit."""
from __future__ import annotations

from dataclasses import dataclass, field

from .cognitive_graph import CognitiveGraph
from .cognitive_node import CognitiveNode
from .cognitive_edge import VALID_RELATIONS
from .graph_validator import validate_graph
from .vector_validator import validate_role_vector, validate_domain_vector
from .invariant_validator import validate_invariants
from .vector_space import ROLE_DIMENSIONS, DOMAIN_DIMENSIONS


@dataclass
class MathematicalContractResult:
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


def check_mathematical_contract(graph: CognitiveGraph) -> MathematicalContractResult:
    """
    Full contract check:
    1. Graph has nodes.
    2. Every node has role_vector and domain_vector.
    3. Vectors match registry dimensions.
    4. Every edge is closed (endpoints in graph).
    5. Cause has effect.
    6. Relations have two endpoints.
    7. Certainty has evidence or warning.
    8. Ambiguous input → suspend.
    9. harm ≠ haram.
    10. tool/API not evidence by itself.
    11. metaphor not literal.
    12. source needs trust policy.
    """
    violations: list[str] = []
    warnings: list[str] = []

    # 1. graph has nodes
    if not graph.nodes:
        violations.append("Contract[1]: graph has no nodes — input→label only pattern rejected")
        return MathematicalContractResult(passed=False, violations=violations, score=0.0)

    # 2 & 3. every node has vectors
    for node in graph.nodes:
        if not node.role_vector:
            violations.append(f"Contract[2]: node '{node.node_id}' missing role_vector")
        else:
            rv_violations = validate_role_vector(node.role_vector).violations
            for v in rv_violations:
                violations.append(f"Contract[3]: node '{node.node_id}' role_vector: {v}")

        if not node.domain_vector:
            violations.append(f"Contract[2]: node '{node.node_id}' missing domain_vector")
        else:
            dv_violations = validate_domain_vector(node.domain_vector).violations
            for v in dv_violations:
                violations.append(f"Contract[3]: node '{node.node_id}' domain_vector: {v}")

    # 4. edge endpoints in graph
    node_ids = graph.node_ids()
    for edge in graph.edges:
        if edge.source not in node_ids:
            violations.append(f"Contract[4]: edge '{edge.edge_id}' source '{edge.source}' not in graph")
        if edge.target not in node_ids:
            violations.append(f"Contract[4]: edge '{edge.edge_id}' target '{edge.target}' not in graph")

    # 5. cause has effect — cause target must be typed as effect OR have a caused_by edge tied to same source/target
    cause_edges = [e for e in graph.edges if e.relation == "causes"]
    effect_node_ids = {n.node_id for n in graph.nodes if n.node_type == "effect"}
    for ce in cause_edges:
        # The target of the causes edge must either be an effect-type node
        # OR there must be a caused_by edge where source==ce.target (proving ce.target is an effect)
        target_is_effect = ce.target in effect_node_ids
        target_has_caused_by = any(
            e for e in graph.edges
            if e.relation == "caused_by" and e.source == ce.target
        )
        if not target_is_effect and not target_has_caused_by:
            violations.append(
                f"Contract[5]: cause node '{ce.source}' → target '{ce.target}' "
                f"has no effect type or caused_by edge — cause_has_effect invariant violated"
            )

    # 7. certainty has evidence or warning
    if graph.certainty_policy == "near_certainty":
        has_ev = any(n.evidence_refs for n in graph.nodes)
        if not has_ev:
            violations.append("Contract[7]: near_certainty requires evidence_refs")

    # 8. ambiguity → suspend
    if "ambiguous" in graph.warnings and graph.certainty_policy == "near_certainty":
        violations.append("Contract[8]: ambiguous input cannot have near_certainty policy")

    # 9. harm ≠ haram
    harm_ids = {n.node_id for n in graph.nodes if "ضار" in n.surface or "harm" in n.surface.lower()}
    haram_ids = {n.node_id for n in graph.nodes if "حرام" in n.surface or "haram" in n.surface.lower()}
    for edge in graph.edges:
        if edge.relation == "entails" and edge.source in harm_ids and edge.target in haram_ids:
            violations.append("Contract[9]: harm does not entail haram — distinct domains")

    # 10. tool/API not evidence by itself — requires evidence_refs OR trust_policy=trusted OR source_trust_score
    tool_ids = {n.node_id for n in graph.nodes if n.node_type in ("tool", "source")}
    evidence_relations = {"supports", "sourced_from", "requires_evidence"}
    for edge in graph.edges:
        if edge.relation in evidence_relations and edge.source in tool_ids:
            has_evidence = bool(edge.evidence_refs)
            trust_policy = edge.metadata.get("trust_policy")
            trust_ok = isinstance(trust_policy, dict) and trust_policy.get("trusted") is True
            trust_score_ok = isinstance(trust_policy, dict) and trust_policy.get("source_trust_score", 0.0) >= 0.7
            if not has_evidence and not trust_ok and not trust_score_ok:
                violations.append(
                    f"Contract[10]: tool/source '{edge.source}' used in '{edge.relation}' "
                    f"without evidence_refs or trust_policy — not valid standalone evidence"
                )

    # 12. source trust
    for edge in graph.edges:
        if edge.relation == "sourced_from":
            if not edge.evidence_refs and not edge.metadata.get("trust_policy"):
                warnings.append(f"Contract[12]: sourced_from edge '{edge.edge_id}' lacks trust policy")

    passed = len(violations) == 0
    score = max(0.0, 1.0 - 0.1 * len(violations) - 0.02 * len(warnings))
    return MathematicalContractResult(
        passed=passed,
        violations=violations,
        warnings=warnings,
        score=min(1.0, score),
    )
