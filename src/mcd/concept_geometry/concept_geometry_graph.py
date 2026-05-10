"""ConceptGeometryGraph — typed graph of Jamid/Mushtaq concept geometry nodes and edges."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional


NODE_TYPES = {
    "JamidEssenceNode", "MushtaqNode", "RootFamilyNode",
    "PatternOperatorNode", "MasdarEventNode", "ConceptCenterNode",
    "AttributeNode", "EventNode", "AgencyNode", "PatienthoodNode",
    "InstrumentNode", "PlaceNode", "TimeNode", "NisbaNode",
}

EDGE_TYPES = {
    "has_essence", "belongs_to_genus", "has_species", "has_differentia",
    "derived_from_root", "has_pattern", "folds_event",
    "projects_agency", "projects_patienthood", "projects_instrument",
    "projects_place", "projects_time", "attributes_to_domain",
    "binds_attribute", "contributes_to_concept_center",
}


@dataclass
class CGNode:
    node_id: str
    node_type: str
    label: str
    attrs: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"node_id": self.node_id, "node_type": self.node_type,
                "label": self.label, **self.attrs}


@dataclass
class CGEdge:
    source: str
    target: str
    edge_type: str
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {"source": self.source, "target": self.target,
                "edge_type": self.edge_type, "weight": self.weight}


@dataclass
class ConceptGeometryGraph:
    graph_id: str
    word: str
    nodes: list[CGNode] = field(default_factory=list)
    edges: list[CGEdge] = field(default_factory=list)

    def add_node(self, node_type: str, label: str, **attrs) -> str:
        nid = f"N-{uuid.uuid4().hex[:8]}"
        self.nodes.append(CGNode(node_id=nid, node_type=node_type, label=label, attrs=attrs))
        return nid

    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0) -> None:
        assert edge_type in EDGE_TYPES, f"Unknown edge type: {edge_type}"
        self.edges.append(CGEdge(source=source, target=target, edge_type=edge_type, weight=weight))

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "word": self.word,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Concept Geometry Graph: {self.word}",
            f"",
            f"Graph ID: `{self.graph_id}`",
            f"Nodes: {len(self.nodes)}  |  Edges: {len(self.edges)}",
            "",
            "## Nodes",
        ]
        for n in self.nodes:
            lines.append(f"- `{n.node_id}` [{n.node_type}] **{n.label}**")
        lines += ["", "## Edges"]
        for e in self.edges:
            lines.append(f"- `{e.source}` —[{e.edge_type}]→ `{e.target}` (w={e.weight})")
        return "\n".join(lines)


class ConceptGeometryGraphBuilder:
    """Build a ConceptGeometryGraph for a given word."""

    def build_for_jamid(self, word: str, jamid_essence) -> ConceptGeometryGraph:
        """Build graph for a Jamid word."""
        g = ConceptGeometryGraph(graph_id=f"CGG-{uuid.uuid4().hex[:8]}", word=word)
        je_nid = g.add_node("JamidEssenceNode", word,
                             essence_type=jamid_essence.essence_type.value if hasattr(jamid_essence.essence_type, "value") else str(jamid_essence.essence_type))
        genus_nid = g.add_node("AttributeNode", jamid_essence.genus)
        g.add_edge(je_nid, genus_nid, "belongs_to_genus")
        if jamid_essence.species:
            sp_nid = g.add_node("AttributeNode", jamid_essence.species)
            g.add_edge(je_nid, sp_nid, "has_species")
        for d in jamid_essence.differentia:
            d_nid = g.add_node("AttributeNode", d)
            g.add_edge(je_nid, d_nid, "has_differentia")
        cc_nid = g.add_node("ConceptCenterNode", f"CC({word})")
        g.add_edge(je_nid, cc_nid, "has_essence")
        return g

    def build_for_mushtaq(self, word: str, mushtaq_unit) -> ConceptGeometryGraph:
        """Build graph for a Mushtaq word."""
        from mcd.concept_geometry.mushtaq_schema import ProjectedRelation
        g = ConceptGeometryGraph(graph_id=f"CGG-{uuid.uuid4().hex[:8]}", word=word)
        mu_nid = g.add_node("MushtaqNode", word,
                             derivation_type=mushtaq_unit.derivation_type.value if hasattr(mushtaq_unit.derivation_type, "value") else str(mushtaq_unit.derivation_type))
        if mushtaq_unit.root:
            r_nid = g.add_node("RootFamilyNode", mushtaq_unit.root)
            g.add_edge(mu_nid, r_nid, "derived_from_root")
        if mushtaq_unit.pattern:
            p_nid = g.add_node("PatternOperatorNode", mushtaq_unit.pattern)
            g.add_edge(mu_nid, p_nid, "has_pattern")
        if mushtaq_unit.folded_event:
            ev_nid = g.add_node("MasdarEventNode", mushtaq_unit.folded_event)
            g.add_edge(mu_nid, ev_nid, "folds_event")
        rel = mushtaq_unit.projected_relation
        edge_map = {
            ProjectedRelation.AGENT_OF: ("AgencyNode", "projects_agency"),
            ProjectedRelation.PATIENT_OF: ("PatienthoodNode", "projects_patienthood"),
            ProjectedRelation.INSTRUMENT_OF: ("InstrumentNode", "projects_instrument"),
            ProjectedRelation.PLACE_OF: ("PlaceNode", "projects_place"),
            ProjectedRelation.TIME_OF: ("TimeNode", "projects_time"),
            ProjectedRelation.ATTRIBUTED_TO: ("NisbaNode", "attributes_to_domain"),
        }
        if rel in edge_map:
            ntype, etype = edge_map[rel]
            rel_nid = g.add_node(ntype, rel.value)
            g.add_edge(mu_nid, rel_nid, etype)
        cc_nid = g.add_node("ConceptCenterNode", f"CC({mushtaq_unit.folded_event or word})")
        g.add_edge(mu_nid, cc_nid, "contributes_to_concept_center")
        return g
