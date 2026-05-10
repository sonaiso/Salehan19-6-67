"""MurabGraph — graph representation of I'rab analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MurabUnitNode:
    node_id: str
    node_type: str = "MurabUnitNode"
    unit_id: str = ""
    surface: str = ""
    word_type: str = ""

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "unit_id": self.unit_id,
            "surface": self.surface,
            "word_type": self.word_type,
        }


@dataclass
class IrabCaseNode:
    node_id: str
    node_type: str = "IrabCaseNode"
    case_id: str = ""

    def to_dict(self) -> dict:
        return {"node_id": self.node_id, "node_type": self.node_type, "case_id": self.case_id}


@dataclass
class MarkerNode:
    node_id: str
    node_type: str = "MarkerNode"
    marker_id: str = ""

    def to_dict(self) -> dict:
        return {"node_id": self.node_id, "node_type": self.node_type, "marker_id": self.marker_id}


@dataclass
class GoverningFactorNode:
    node_id: str
    node_type: str = "GoverningFactorNode"
    factor_id: str = ""
    surface: str = ""

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "factor_id": self.factor_id,
            "surface": self.surface,
        }


@dataclass
class SyntacticRoleNode:
    node_id: str
    node_type: str = "SyntacticRoleNode"
    role: str = ""

    def to_dict(self) -> dict:
        return {"node_id": self.node_id, "node_type": self.node_type, "role": self.role}


@dataclass
class SemanticRoleNode:
    node_id: str
    node_type: str = "SemanticRoleNode"
    role: str = ""

    def to_dict(self) -> dict:
        return {"node_id": self.node_id, "node_type": self.node_type, "role": self.role}


@dataclass
class RelationNode:
    node_id: str
    node_type: str = "RelationNode"
    relation_type: str = ""

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "relation_type": self.relation_type,
        }


@dataclass
class MurabEdge:
    edge_id: str
    source_id: str
    target_id: str
    edge_type: str  # has_case|has_marker|governed_by|projects_role|agent_of|
                    # patient_of|predicate_of|subject_of|possessor_of|
                    # specified_by|modifies|follows|time_of|place_of|
                    # state_of|distinguishes|excepted_from|restricted_by

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
        }


@dataclass
class MurabGraph:
    graph_id: str
    sentence: str
    nodes: list[Any] = field(default_factory=list)
    edges: list[MurabEdge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "sentence": self.sentence,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MurabGraph":
        return cls(
            graph_id=d["graph_id"],
            sentence=d.get("sentence", ""),
            nodes=d.get("nodes", []),
            edges=[MurabEdge(**e) for e in d.get("edges", [])],
        )


class MurabGraphBuilder:
    """Builds a MurabGraph from a list of MurabUnit objects and a sentence string."""

    def build(self, units: list, sentence: str) -> MurabGraph:
        import uuid
        graph_id = str(uuid.uuid4())
        nodes: list = []
        edges: list[MurabEdge] = []
        edge_counter = 0

        for unit in units:
            # Unit node
            unit_node = MurabUnitNode(
                node_id=f"unit_{unit.unit_id}",
                unit_id=unit.unit_id,
                surface=unit.surface,
                word_type=unit.word_type,
            )
            nodes.append(unit_node)

            # IrabCase node + edge
            case_node = IrabCaseNode(
                node_id=f"case_{unit.unit_id}",
                case_id=unit.irab_case,
            )
            nodes.append(case_node)
            edges.append(MurabEdge(
                edge_id=f"e{edge_counter}",
                source_id=unit_node.node_id,
                target_id=case_node.node_id,
                edge_type="has_case",
            ))
            edge_counter += 1

            # Marker node + edge
            marker_node = MarkerNode(
                node_id=f"marker_{unit.unit_id}",
                marker_id=unit.irab_marker,
            )
            nodes.append(marker_node)
            edges.append(MurabEdge(
                edge_id=f"e{edge_counter}",
                source_id=unit_node.node_id,
                target_id=marker_node.node_id,
                edge_type="has_marker",
            ))
            edge_counter += 1

            # Governing factor node + edge
            if unit.governing_factor_id:
                gf_node = GoverningFactorNode(
                    node_id=f"gf_{unit.unit_id}",
                    factor_id=unit.governing_factor_id,
                )
                nodes.append(gf_node)
                edges.append(MurabEdge(
                    edge_id=f"e{edge_counter}",
                    source_id=unit_node.node_id,
                    target_id=gf_node.node_id,
                    edge_type="governed_by",
                ))
                edge_counter += 1

            # Syntactic role node + edge
            if unit.syntactic_role:
                syn_node = SyntacticRoleNode(
                    node_id=f"syn_{unit.unit_id}",
                    role=unit.syntactic_role,
                )
                nodes.append(syn_node)
                edges.append(MurabEdge(
                    edge_id=f"e{edge_counter}",
                    source_id=unit_node.node_id,
                    target_id=syn_node.node_id,
                    edge_type="projects_role",
                ))
                edge_counter += 1

            # Semantic role node + edge
            if unit.semantic_role and unit.semantic_role != "unknown":
                sem_map = {
                    "agent": "agent_of",
                    "patient": "patient_of",
                    "predicate": "predicate_of",
                    "subject": "subject_of",
                    "possessor": "possessor_of",
                }
                sem_node = SemanticRoleNode(
                    node_id=f"sem_{unit.unit_id}",
                    role=unit.semantic_role,
                )
                nodes.append(sem_node)
                edges.append(MurabEdge(
                    edge_id=f"e{edge_counter}",
                    source_id=unit_node.node_id,
                    target_id=sem_node.node_id,
                    edge_type=sem_map.get(unit.semantic_role, "projects_role"),
                ))
                edge_counter += 1

            # Relation edges from unit
            for rel in unit.relation_edges:
                edges.append(MurabEdge(
                    edge_id=f"e{edge_counter}",
                    source_id=unit_node.node_id,
                    target_id=rel.get("target_id", ""),
                    edge_type=rel.get("edge_type", "dep"),
                ))
                edge_counter += 1

        return MurabGraph(
            graph_id=graph_id,
            sentence=sentence,
            nodes=nodes,
            edges=edges,
        )
