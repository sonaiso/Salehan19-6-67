"""Serializers for the morphosemantics package.

Provides JSON and Markdown serialization for the main morphosemantic
data structures, following the project pattern of to_dict() + serializer.
"""
from __future__ import annotations

import json
from typing import Union

from mcd.morphosemantics.folded_word_graph import FoldedWordGraph
from mcd.morphosemantics.concept_center import ConceptCenter
from mcd.morphosemantics.pattern_operator_registry import PatternOperator
from mcd.morphosemantics.root_ontology import RootNode
from mcd.morphosemantics.root_family_graph import RootFamilyGraph


def folded_word_graph_to_json(graph: FoldedWordGraph, indent: int = 2) -> str:
    return json.dumps(graph.to_dict(), ensure_ascii=False, indent=indent)


def concept_center_to_json(cc: ConceptCenter, indent: int = 2) -> str:
    return json.dumps(cc.to_dict(), ensure_ascii=False, indent=indent)


def pattern_operator_to_markdown(op: PatternOperator) -> str:
    lines = [
        f"# Pattern Operator — {op.pattern_form}",
        "",
        f"**ID:** {op.pattern_id}  |  **Family:** {op.family}  |  **Certainty:** {op.certainty_policy}",
        "",
        "## Operator Vector",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]
    for k, v in sorted(op.operator_vector.items(), key=lambda x: -x[1]):
        if v > 0:
            lines.append(f"| {k} | {v:.2f} |")
    lines += [
        "",
        "## Examples",
        "",
    ]
    for ex in op.examples:
        lines.append(f"- {ex}")
    return "\n".join(lines)


def root_node_to_json(root: RootNode, indent: int = 2) -> str:
    return json.dumps(root.to_dict(), ensure_ascii=False, indent=indent)


def root_family_to_json(graph: RootFamilyGraph, indent: int = 2) -> str:
    return json.dumps(graph.to_dict(), ensure_ascii=False, indent=indent)
