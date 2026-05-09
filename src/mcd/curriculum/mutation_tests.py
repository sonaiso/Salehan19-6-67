"""MutationTests — tests that mutate golden examples and verify validators fail them."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Callable

from .cognitive_graph import CognitiveGraph
from .cognitive_node import CognitiveNode
from .cognitive_edge import CognitiveEdge
from .mathematical_contract import check_mathematical_contract
from .invariant_validator import validate_invariants
from .vector_validator import validate_role_vector, validate_domain_vector
from .graph_validator import validate_graph
from .vector_space import zero_role_vector, zero_domain_vector
from .golden_examples import load_golden_examples, GoldenExample


MUTATION_TYPES: list[str] = [
    "remove_role_vector",
    "remove_domain_vector",
    "remove_edge_target",
    "remove_edge_source",
    "remove_effect_for_cause",
    "set_near_certainty_without_evidence",
    "mark_api_as_evidence_without_trust",
    "remove_domain_from_level9",
    "remove_graph_from_level10",
    "replace_structured_frame_with_label_only",
]


@dataclass
class MutationTestResult:
    mutation_name: str
    expected_to_fail: bool
    actually_failed: bool
    passed: bool
    explanation: str

    def to_dict(self) -> dict:
        return {
            "mutation_name": self.mutation_name,
            "expected_to_fail": self.expected_to_fail,
            "actually_failed": self.actually_failed,
            "passed": self.passed,
            "explanation": self.explanation,
        }


@dataclass
class MutationTestReport:
    results: list[MutationTestResult] = field(default_factory=list)
    pass_rate: float = 0.0
    total: int = 0
    passed: int = 0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "pass_rate": round(self.pass_rate, 4),
            "results": [r.to_dict() for r in self.results],
        }


def _build_graph_from_golden(ex: GoldenExample) -> CognitiveGraph:
    """Build a valid CognitiveGraph from a GoldenExample with proper vectors."""
    valid_node_types = [
        "thing", "property", "action", "relation", "cause", "effect",
        "instrument", "time", "place", "evidence", "claim", "judgment",
        "source", "tool", "domain",
    ]
    type_map = {"agent": "thing", "patient": "thing", "concept": "thing"}

    nodes = []
    for nd in ex.expected_nodes:
        nid = nd.get("id", nd.get("node_id", "unknown"))
        ntype = nd.get("type", nd.get("node_type", "thing"))
        ntype = type_map.get(ntype, ntype)
        if ntype not in valid_node_types:
            ntype = "thing"
        rv = zero_role_vector()
        rv[ntype] = 1.0
        dv = zero_domain_vector()
        for d in ex.expected_domains:
            if d in dv:
                dv[d] = 1.0
        if not any(dv.values()):
            dv["education"] = 1.0
        nodes.append(CognitiveNode(
            node_id=nid,
            surface=nid,
            normalized=nid,
            node_type=ntype,
            role_vector=rv,
            domain_vector=dv,
            evidence_refs=ex.evidence_need,
        ))

    valid_rels = [
        "has_property", "agent_of", "patient_of", "instrument_of",
        "time_of", "place_of", "causes", "caused_by", "supports",
        "contradicts", "qualifies", "restricts", "entails",
        "requires_evidence", "has_certainty_policy", "belongs_to_domain",
        "uses_tool", "sourced_from", "not_equivalent_to",
    ]
    node_ids = {n.node_id for n in nodes}
    edges = []
    for i, ed in enumerate(ex.expected_edges):
        src = ed.get("source", "")
        tgt = ed.get("target", "")
        rel = ed.get("relation", "has_property")
        if src not in node_ids or tgt not in node_ids:
            continue
        if rel not in valid_rels:
            rel = "has_property"
        edges.append(CognitiveEdge(
            edge_id=f"E{i:03d}",
            source=src,
            relation=rel,
            target=tgt,
        ))

    rv_sum = zero_role_vector()
    for n in nodes:
        for k, v in n.role_vector.items():
            rv_sum[k] = rv_sum.get(k, 0.0) + v
    total_rv = sum(rv_sum.values())
    root_vector = {k: v / total_rv for k, v in rv_sum.items()} if total_rv > 0 else rv_sum

    dv_sum = zero_domain_vector()
    for n in nodes:
        for k, v in n.domain_vector.items():
            dv_sum[k] = dv_sum.get(k, 0.0) + v
    total_dv = sum(dv_sum.values())
    domain_summary = {k: v / total_dv for k, v in dv_sum.items()} if total_dv > 0 else dv_sum

    valid_certainty = [
        "certain_knowledge", "probable_knowledge", "possible_knowledge",
        "insufficient_evidence", "near_certainty", "suspend_judgment",
    ]
    cp = ex.certainty_policy if ex.certainty_policy in valid_certainty else "probable_knowledge"

    return CognitiveGraph(
        graph_id=ex.example_id,
        nodes=nodes,
        edges=edges,
        root_vector=root_vector,
        domain_summary=domain_summary,
        evidence_status="sufficient" if ex.evidence_need else "missing",
        certainty_policy=cp,
    )


def _graph_fails_contract(graph: CognitiveGraph) -> bool:
    """Return True if the graph fails any contract or invariant check."""
    contract = check_mathematical_contract(graph)
    if not contract.passed:
        return True
    inv = validate_invariants(graph)
    if not inv.passed:
        return True
    gv = validate_graph(graph)
    if not gv.passed:
        return True
    return False


# ---- Mutation functions ----

def _mutate_remove_role_vector(graph: CognitiveGraph) -> CognitiveGraph:
    """Remove role_vector from first node."""
    if not graph.nodes:
        return graph
    node = graph.nodes[0]
    mutated = CognitiveNode(
        node_id=node.node_id, surface=node.surface, normalized=node.normalized,
        node_type=node.node_type, grounding_status=node.grounding_status,
        role_vector={},  # removed
        domain_vector=node.domain_vector,
        evidence_refs=node.evidence_refs, certainty=node.certainty, metadata=node.metadata,
    )
    return CognitiveGraph(
        graph_id=graph.graph_id,
        nodes=[mutated] + graph.nodes[1:],
        edges=graph.edges,
        root_vector=graph.root_vector,
        domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status,
        certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_domain_vector(graph: CognitiveGraph) -> CognitiveGraph:
    """Remove domain_vector from first node."""
    if not graph.nodes:
        return graph
    node = graph.nodes[0]
    mutated = CognitiveNode(
        node_id=node.node_id, surface=node.surface, normalized=node.normalized,
        node_type=node.node_type, grounding_status=node.grounding_status,
        role_vector=node.role_vector,
        domain_vector={},  # removed
        evidence_refs=node.evidence_refs, certainty=node.certainty, metadata=node.metadata,
    )
    return CognitiveGraph(
        graph_id=graph.graph_id,
        nodes=[mutated] + graph.nodes[1:],
        edges=graph.edges,
        root_vector=graph.root_vector,
        domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status,
        certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_edge_target(graph: CognitiveGraph) -> CognitiveGraph:
    """Break first edge by pointing to non-existent target."""
    if not graph.edges:
        return graph
    edge = graph.edges[0]
    broken = CognitiveEdge(
        edge_id=edge.edge_id, source=edge.source,
        relation=edge.relation, target="__nonexistent__",
        qualifier=edge.qualifier, evidence_refs=edge.evidence_refs,
        certainty=edge.certainty, metadata=edge.metadata,
    )
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=graph.nodes,
        edges=[broken] + graph.edges[1:],
        root_vector=graph.root_vector, domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status, certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_edge_source(graph: CognitiveGraph) -> CognitiveGraph:
    """Break first edge by setting non-existent source."""
    if not graph.edges:
        return graph
    edge = graph.edges[0]
    broken = CognitiveEdge(
        edge_id=edge.edge_id, source="__nonexistent__",
        relation=edge.relation, target=edge.target,
        qualifier=edge.qualifier, evidence_refs=edge.evidence_refs,
        certainty=edge.certainty, metadata=edge.metadata,
    )
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=graph.nodes,
        edges=[broken] + graph.edges[1:],
        root_vector=graph.root_vector, domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status, certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_effect_for_cause(graph: CognitiveGraph) -> CognitiveGraph:
    """Add a cause node with a causes edge to a non-effect target — violates cause_has_effect."""
    cause_node = CognitiveNode(
        node_id="mut_cause", surface="mut_cause", normalized="mut_cause",
        node_type="cause",
        role_vector={**zero_role_vector(), "cause": 1.0},
        domain_vector={**zero_domain_vector(), "education": 1.0},
    )
    non_effect_node = CognitiveNode(
        node_id="mut_thing", surface="mut_thing", normalized="mut_thing",
        node_type="thing",
        role_vector={**zero_role_vector(), "thing": 1.0},
        domain_vector={**zero_domain_vector(), "education": 1.0},
    )
    bad_edge = CognitiveEdge(
        edge_id="mut_cause_edge", source="mut_cause",
        relation="causes", target="mut_thing",
    )
    return CognitiveGraph(
        graph_id=graph.graph_id,
        nodes=graph.nodes + [cause_node, non_effect_node],
        edges=graph.edges + [bad_edge],
        root_vector=graph.root_vector, domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status, certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_near_certainty_without_evidence(graph: CognitiveGraph) -> CognitiveGraph:
    """Set near_certainty on a graph with no evidence."""
    nodes_no_ev = [
        CognitiveNode(
            node_id=n.node_id, surface=n.surface, normalized=n.normalized,
            node_type=n.node_type, grounding_status=n.grounding_status,
            role_vector=n.role_vector, domain_vector=n.domain_vector,
            evidence_refs=[],  # strip evidence
            certainty=n.certainty, metadata=n.metadata,
        )
        for n in graph.nodes
    ]
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=nodes_no_ev, edges=graph.edges,
        root_vector=graph.root_vector, domain_summary=graph.domain_summary,
        evidence_status="missing",
        certainty_policy="near_certainty",
        warnings=graph.warnings,
    )


def _mutate_api_as_evidence_without_trust(graph: CognitiveGraph) -> CognitiveGraph:
    """Add a tool node that supports without trust_policy or evidence_refs."""
    tool_node = CognitiveNode(
        node_id="mut_api", surface="mut_api", normalized="mut_api",
        node_type="tool",
        role_vector={**zero_role_vector(), "tool": 1.0},
        domain_vector={**zero_domain_vector(), "technology": 1.0},
    )
    target_node_id = graph.nodes[0].node_id if graph.nodes else "unknown"
    bad_edge = CognitiveEdge(
        edge_id="mut_api_edge", source="mut_api",
        relation="supports", target=target_node_id,
        evidence_refs=[],  # no evidence
        metadata={},  # no trust_policy
    )
    return CognitiveGraph(
        graph_id=graph.graph_id,
        nodes=graph.nodes + [tool_node],
        edges=graph.edges + [bad_edge],
        root_vector=graph.root_vector, domain_summary=graph.domain_summary,
        evidence_status=graph.evidence_status, certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_domain_from_level9(graph: CognitiveGraph) -> CognitiveGraph:
    """Remove domain_summary (domain info) from graph — simulates missing domain in level9."""
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=graph.nodes, edges=graph.edges,
        root_vector=graph.root_vector,
        domain_summary={},  # removed
        evidence_status=graph.evidence_status, certainty_policy=graph.certainty_policy,
        warnings=graph.warnings,
    )


def _mutate_remove_graph_from_level10(graph: CognitiveGraph) -> CognitiveGraph:
    """Simulate level10 with no nodes or edges — pure label without structure."""
    if not graph.nodes:
        return graph
    # Keep only one node with no vectors and no edges
    bare_node = CognitiveNode(
        node_id="label_only", surface="label_only", normalized="label_only",
        node_type="thing",
        role_vector={},
        domain_vector={},
    )
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=[bare_node], edges=[],
        root_vector={}, domain_summary={},
        evidence_status="missing", certainty_policy="probable_knowledge",
    )


def _mutate_label_only(graph: CognitiveGraph) -> CognitiveGraph:
    """Replace entire structure with a label-only node — missing all vectors and edges."""
    bare_node = CognitiveNode(
        node_id="label_only", surface="كلمة", normalized="كلمة",
        node_type="thing",
        role_vector={},
        domain_vector={},
    )
    return CognitiveGraph(
        graph_id=graph.graph_id, nodes=[bare_node], edges=[],
        root_vector={}, domain_summary={},
        evidence_status="missing", certainty_policy="probable_knowledge",
    )


_MUTATION_FUNCTIONS: dict[str, Callable[[CognitiveGraph], CognitiveGraph]] = {
    "remove_role_vector": _mutate_remove_role_vector,
    "remove_domain_vector": _mutate_remove_domain_vector,
    "remove_edge_target": _mutate_remove_edge_target,
    "remove_edge_source": _mutate_remove_edge_source,
    "remove_effect_for_cause": _mutate_remove_effect_for_cause,
    "set_near_certainty_without_evidence": _mutate_near_certainty_without_evidence,
    "mark_api_as_evidence_without_trust": _mutate_api_as_evidence_without_trust,
    "remove_domain_from_level9": _mutate_remove_domain_from_level9,
    "remove_graph_from_level10": _mutate_remove_graph_from_level10,
    "replace_structured_frame_with_label_only": _mutate_label_only,
}


def run_mutation_tests() -> MutationTestReport:
    """
    Run all mutation types against golden examples.
    Each mutation must cause a contract/invariant/graph validation failure.
    """
    golden = load_golden_examples()
    results: list[MutationTestResult] = []

    # Use first available golden example; some mutations need edges so prefer one with edges
    base_ex: GoldenExample | None = None
    base_ex_with_edges: GoldenExample | None = None
    for ex in golden:
        if base_ex is None:
            base_ex = ex
        if ex.expected_edges and base_ex_with_edges is None:
            base_ex_with_edges = ex

    if base_ex is None:
        # No golden examples available: build a synthetic one
        from .cognitive_graph import CognitiveGraph
        base_graph = CognitiveGraph(
            graph_id="synthetic",
            nodes=[CognitiveNode(
                node_id="n1", surface="n1", normalized="n1", node_type="thing",
                role_vector={**zero_role_vector(), "thing": 1.0},
                domain_vector={**zero_domain_vector(), "education": 1.0},
                evidence_refs=["ref1"],
            )],
            edges=[],
            root_vector={**zero_role_vector(), "thing": 1.0},
            domain_summary={**zero_domain_vector(), "education": 1.0},
            evidence_status="sufficient",
            certainty_policy="probable_knowledge",
        )
        base_graph_with_edges = base_graph
    else:
        base_graph = _build_graph_from_golden(base_ex)
        base_graph_with_edges = (
            _build_graph_from_golden(base_ex_with_edges)
            if base_ex_with_edges else base_graph
        )

    edge_dependent = {"remove_edge_target", "remove_edge_source"}

    for mutation_name in MUTATION_TYPES:
        fn = _MUTATION_FUNCTIONS[mutation_name]
        src_graph = base_graph_with_edges if mutation_name in edge_dependent else base_graph
        try:
            mutated = fn(src_graph)
            failed = _graph_fails_contract(mutated)
        except Exception as exc:
            failed = True  # unexpected exception counts as failure
            explanation = f"Exception during mutation '{mutation_name}': {exc}"
        else:
            explanation = (
                "mutation correctly detected — validators failed"
                if failed
                else "mutation NOT detected — validators did not fail (bug)"
            )

        results.append(MutationTestResult(
            mutation_name=mutation_name,
            expected_to_fail=True,
            actually_failed=failed,
            passed=failed,  # pass = mutation was caught
            explanation=explanation,
        ))

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total if total > 0 else 0.0

    return MutationTestReport(
        results=results,
        pass_rate=pass_rate,
        total=total,
        passed=passed,
    )
