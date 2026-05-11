"""MabniGraphBuilder — builds a graph of Mabni operator relationships."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MabniNode:
    node_id: str
    operator_id: str
    surface: str
    node_type: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "operator_id": self.operator_id,
            "surface": self.surface,
            "node_type": self.node_type,
            "properties": self.properties,
        }


@dataclass
class MabniEdge:
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "properties": self.properties,
        }


@dataclass
class MabniGraph:
    graph_id: str
    nodes: list[MabniNode] = field(default_factory=list)
    edges: list[MabniEdge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }


class MabniGraphBuilder:
    """Builds a graph of Mabni operator relationships from unfolded results."""

    def __init__(self) -> None:
        self._node_counter = 0
        self._edge_counter = 0

    def _next_node_id(self) -> str:
        self._node_counter += 1
        return f"N{self._node_counter:04d}"

    def _next_edge_id(self) -> str:
        self._edge_counter += 1
        return f"E{self._edge_counter:04d}"

    def build(self, unfold_result: dict, graph_id: str = "mabni_graph") -> MabniGraph:
        """Build a MabniGraph from a MabniUnfoldResult dict.

        Counters are reset at the start of each call so that node/edge IDs are
        deterministic per-invocation regardless of how many times this builder
        has been reused in the same process.
        """
        self._node_counter = 0
        self._edge_counter = 0
        graph = MabniGraph(graph_id=graph_id)
        node_index: dict[str, str] = {}

        # Root node for the utterance
        root_id = self._next_node_id()
        root_node = MabniNode(
            node_id=root_id,
            operator_id="ROOT",
            surface=unfold_result.get("text", ""),
            node_type="utterance_root",
            properties={},
        )
        graph.nodes.append(root_node)
        node_index["ROOT"] = root_id

        # Process each operator result
        for key, value in unfold_result.items():
            if not isinstance(value, dict):
                continue
            if "operator_id" not in value and "surface" not in value:
                continue

            node_id = self._next_node_id()
            operator_id = value.get("operator_id", key)
            surface = value.get("surface", "")
            node_type = key

            node = MabniNode(
                node_id=node_id,
                operator_id=operator_id,
                surface=surface,
                node_type=node_type,
                properties={k: v for k, v in value.items() if k not in ("operator_id", "surface")},
            )
            graph.nodes.append(node)
            node_index[key] = node_id

            # Edge from root to this operator node
            edge = MabniEdge(
                edge_id=self._next_edge_id(),
                source_id=root_id,
                target_id=node_id,
                relation="contains_operator",
            )
            graph.edges.append(edge)

        # Add scope dependency edges where applicable
        for key, value in unfold_result.items():
            if isinstance(value, dict) and value.get("scope") and key in node_index:
                scope_key = value["scope"]
                if scope_key in node_index:
                    edge = MabniEdge(
                        edge_id=self._next_edge_id(),
                        source_id=node_index[key],
                        target_id=node_index[scope_key],
                        relation="takes_scope_over",
                    )
                    graph.edges.append(edge)

        return graph
