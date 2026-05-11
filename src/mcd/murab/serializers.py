"""Serializers — JSON and Markdown output for MurabUnit and MurabGraph."""
from __future__ import annotations

import json

from mcd.murab.murab_schema import MurabUnit
from mcd.murab.murab_report import MurabReport


def murab_units_to_json(units: list[MurabUnit]) -> str:
    return json.dumps([u.to_dict() for u in units], ensure_ascii=False, indent=2)


def murab_units_to_markdown(units: list[MurabUnit], sentence: str) -> str:
    return MurabReport().to_markdown(units, sentence)


def murab_graph_to_json(graph) -> str:
    return json.dumps(graph.to_dict(), ensure_ascii=False, indent=2)


def murab_graph_to_markdown(graph) -> str:
    lines = [
        f"# مخطط الإعراب (MurabGraph)",
        f"",
        f"**الجملة:** {graph.sentence}",
        f"**معرّف المخطط:** {graph.graph_id}",
        f"",
        f"## العقد ({len(graph.nodes)})",
    ]
    for n in graph.nodes:
        d = n.to_dict() if hasattr(n, "to_dict") else n
        lines.append(f"- `{d.get('node_id', '')}` [{d.get('node_type', '')}]")

    lines.append(f"")
    lines.append(f"## الحواف ({len(graph.edges)})")
    for e in graph.edges:
        d = e.to_dict() if hasattr(e, "to_dict") else e
        lines.append(
            f"- `{d.get('source_id', '')}` --[{d.get('edge_type', '')}]--> "
            f"`{d.get('target_id', '')}`"
        )

    return "\n".join(lines)
