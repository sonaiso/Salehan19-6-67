"""FoldedWordGraph — the core data structure of Phase 7.3.

Every Arabic word is a *folded cognitive graph*: it compresses root semantics,
pattern operator effects, role assignments, and domain activations into a
single surface form.  The FoldedWordGraph makes this compression explicit as
a graph of nodes and typed edges, together with role/domain/event vectors.

Edge types:
  has_root, has_pattern, folds_agency, folds_patienthood, folds_causation,
  folds_instrument, folds_time, folds_place, folds_nisba, folds_comparison,
  folds_multiplication, folds_transformation
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional


EDGE_TYPES = {
    "has_root", "has_pattern",
    "folds_agency", "folds_patienthood", "folds_causation",
    "folds_instrument", "folds_time", "folds_place",
    "folds_nisba", "folds_comparison", "folds_multiplication",
    "folds_transformation",
}


@dataclass
class FoldedWordGraph:
    word: str
    root_candidates: list[str]
    pattern_candidates: list[str]
    selected_root: str
    selected_pattern: str
    folded_nodes: list[dict]
    folded_edges: list[dict]
    role_vector: dict[str, float]
    domain_vector: dict[str, float]
    event_vector: dict[str, float]
    certainty_policy: str
    trace_ids: list[str]

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "root_candidates": self.root_candidates,
            "pattern_candidates": self.pattern_candidates,
            "selected_root": self.selected_root,
            "selected_pattern": self.selected_pattern,
            "folded_nodes": self.folded_nodes,
            "folded_edges": self.folded_edges,
            "role_vector": self.role_vector,
            "domain_vector": self.domain_vector,
            "event_vector": self.event_vector,
            "certainty_policy": self.certainty_policy,
            "trace_ids": self.trace_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FoldedWordGraph":
        return cls(**d)


def _make_node(node_id: str, node_type: str, label: str, **attrs) -> dict:
    return {"node_id": node_id, "node_type": node_type, "label": label, **attrs}


def _make_edge(source: str, target: str, edge_type: str, weight: float = 1.0) -> dict:
    assert edge_type in EDGE_TYPES, f"Unknown edge type: {edge_type}"
    return {"source": source, "target": target, "edge_type": edge_type, "weight": weight}


def build_folded_word_graph(
    word: str,
    root_id: str,
    pattern_id: str,
    role_vector: dict[str, float],
    domain_vector: dict[str, float],
    event_vector: dict[str, float],
    certainty_policy: str = "qiyasi",
    root_candidates: Optional[list[str]] = None,
    pattern_candidates: Optional[list[str]] = None,
) -> FoldedWordGraph:
    """Construct a FoldedWordGraph for a word given its root and pattern."""
    trace_id = f"FWG-{uuid.uuid4().hex[:10]}"

    # Nodes
    word_node = _make_node("N-word", "word", word)
    root_node = _make_node("N-root", "root", root_id)
    pattern_node = _make_node("N-pattern", "pattern", pattern_id)

    nodes = [word_node, root_node, pattern_node]
    edges = [
        _make_edge("N-word", "N-root", "has_root"),
        _make_edge("N-word", "N-pattern", "has_pattern"),
    ]

    # Add role folding edges based on role_vector
    role_edge_map = {
        "agency": "folds_agency",
        "patienthood": "folds_patienthood",
        "causation": "folds_causation",
        "instrument": "folds_instrument",
        "time": "folds_time",
        "place": "folds_place",
        "nisba": "folds_nisba",
        "comparison": "folds_comparison",
        "plurality": "folds_multiplication",
        "mutawaa": "folds_transformation",
    }
    for role_key, edge_type in role_edge_map.items():
        score = role_vector.get(role_key, 0.0)
        if score > 0.3:
            role_node_id = f"N-{role_key}"
            nodes.append(_make_node(role_node_id, "role", role_key))
            edges.append(_make_edge("N-word", role_node_id, edge_type, weight=score))

    return FoldedWordGraph(
        word=word,
        root_candidates=root_candidates or [root_id],
        pattern_candidates=pattern_candidates or [pattern_id],
        selected_root=root_id,
        selected_pattern=pattern_id,
        folded_nodes=nodes,
        folded_edges=edges,
        role_vector=role_vector,
        domain_vector=domain_vector,
        event_vector=event_vector,
        certainty_policy=certainty_policy,
        trace_ids=[trace_id],
    )
