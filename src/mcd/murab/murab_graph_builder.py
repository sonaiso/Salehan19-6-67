"""MurabGraphBuilder — builds relational graph from MurabUnit objects."""
from __future__ import annotations
from dataclasses import dataclass, field
from mcd.murab.murab_schema import MurabUnit


@dataclass
class MurabNode:
    node_id: str
    node_type: str  # murab_unit|irab_case|marker|governing_factor|syntactic_role|semantic_role
    label: str
    attributes: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "attributes": self.attributes,
        }


@dataclass
class MurabEdge:
    source_id: str
    target_id: str
    edge_type: str  # has_case|has_marker|governed_by|projects_role|agent_of|patient_of|...
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "weight": self.weight,
        }


@dataclass
class MurabGraph:
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() if hasattr(n, 'to_dict') else n for n in self.nodes],
            "edges": [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.edges],
        }


class MurabGraphBuilder:
    """Builds a relational graph from a list of MurabUnit objects."""

    def build(self, units: list) -> MurabGraph:
        """Build graph from list of MurabUnit objects."""
        nodes = []
        edges = []

        for unit in units:
            unit_node = MurabNode(
                node_id=unit.unit_id,
                node_type="murab_unit",
                label=unit.surface,
                attributes={"normalized": unit.normalized, "token_id": unit.token_id},
            )
            nodes.append(unit_node)

            case_node_id = f"case_{unit.irab_case}"
            case_node = MurabNode(
                node_id=case_node_id,
                node_type="irab_case",
                label=unit.irab_case,
            )
            if not any(n.node_id == case_node_id for n in nodes):
                nodes.append(case_node)

            edges.append(MurabEdge(
                source_id=unit.unit_id,
                target_id=case_node_id,
                edge_type="has_case",
            ))

            marker_node_id = f"marker_{unit.irab_marker}"
            marker_node = MurabNode(
                node_id=marker_node_id,
                node_type="marker",
                label=unit.irab_marker,
            )
            if not any(n.node_id == marker_node_id for n in nodes):
                nodes.append(marker_node)

            edges.append(MurabEdge(
                source_id=unit.unit_id,
                target_id=marker_node_id,
                edge_type="has_marker",
            ))

            role_node_id = f"role_{unit.syntactic_role}"
            role_node = MurabNode(
                node_id=role_node_id,
                node_type="syntactic_role",
                label=unit.syntactic_role,
            )
            if not any(n.node_id == role_node_id for n in nodes):
                nodes.append(role_node)

            edges.append(MurabEdge(
                source_id=unit.unit_id,
                target_id=role_node_id,
                edge_type="projects_role",
            ))

            if unit.governing_factor_id:
                gf_node_id = f"gf_{unit.governing_factor_id}"
                gf_node = MurabNode(
                    node_id=gf_node_id,
                    node_type="governing_factor",
                    label=unit.governing_factor_id,
                )
                if not any(n.node_id == gf_node_id for n in nodes):
                    nodes.append(gf_node)

                edges.append(MurabEdge(
                    source_id=unit.unit_id,
                    target_id=gf_node_id,
                    edge_type="governed_by",
                ))

        return MurabGraph(nodes=nodes, edges=edges)
