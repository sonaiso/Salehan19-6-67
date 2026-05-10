"""Serializers for MurabUnit and MurabGraph."""
from __future__ import annotations
import json
from mcd.murab.murab_schema import MurabUnit


def murab_unit_to_json(unit: MurabUnit) -> str:
    """Serialize a MurabUnit to JSON string."""
    return json.dumps(unit.to_dict(), ensure_ascii=False, indent=2)


def murab_units_to_json(units: list) -> str:
    """Serialize list of MurabUnit to JSON string."""
    return json.dumps([u.to_dict() for u in units], ensure_ascii=False, indent=2)


def murab_unit_to_markdown(unit: MurabUnit) -> str:
    """Serialize a MurabUnit to markdown."""
    lines = [
        f"## {unit.surface}\n",
        f"- **Unit ID**: {unit.unit_id}",
        f"- **Surface**: {unit.surface}",
        f"- **Normalized**: {unit.normalized}",
        f"- **Word Type**: {unit.word_type}",
        f"- **I'rab Case**: {unit.irab_case}",
        f"- **I'rab Marker**: {unit.irab_marker}",
        f"- **Marker Visibility**: {unit.marker_visibility}",
        f"- **Governing Factor**: {unit.governing_factor_id or 'none'}",
        f"- **Syntactic Role**: {unit.syntactic_role}",
        f"- **Semantic Role**: {unit.semantic_role}",
        f"- **Certainty Policy**: {unit.certainty_policy}",
    ]
    if unit.warnings:
        lines.append(f"- **Warnings**: {', '.join(unit.warnings)}")
    return "\n".join(lines)


def murab_graph_to_json(graph) -> str:
    """Serialize a MurabGraph to JSON string."""
    return json.dumps(graph.to_dict(), ensure_ascii=False, indent=2)


def murab_graph_to_markdown(graph) -> str:
    """Serialize a MurabGraph to markdown summary."""
    lines = [
        "# Mu'rab Graph\n",
        f"**Nodes**: {len(graph.nodes)}",
        f"**Edges**: {len(graph.edges)}\n",
        "## Nodes\n",
    ]
    for node in graph.nodes:
        if hasattr(node, 'node_type'):
            lines.append(f"- [{node.node_type}] **{node.node_id}**: {node.label}")
        else:
            lines.append(f"- {node}")
    lines.append("\n## Edges\n")
    for edge in graph.edges:
        if hasattr(edge, 'edge_type'):
            lines.append(f"- {edge.source_id} --[{edge.edge_type}]--> {edge.target_id}")
        else:
            lines.append(f"- {edge}")
    return "\n".join(lines)
