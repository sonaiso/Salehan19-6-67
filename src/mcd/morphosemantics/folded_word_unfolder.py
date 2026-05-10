"""FoldedWordUnfolder — unfolds a FoldedWordGraph into its semantic components.

The unfolding process reverses the cognitive compression: given a word's
FoldedWordGraph, this module expands it into a structured table of:
  root → radicals → semantic_core
  pattern → operator_vector
  role_vector → primary role
  domain_vector → active domains
  event_vector → event class
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.folded_word_graph import FoldedWordGraph
from mcd.morphosemantics.root_ontology import get_root_by_id
from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry


@dataclass
class UnfoldedRow:
    layer: str  # root|pattern|role|domain|event
    key: str
    value: str
    score: float

    def to_dict(self) -> dict:
        return {"layer": self.layer, "key": self.key, "value": self.value, "score": self.score}


@dataclass
class UnfoldedWordGraph:
    word: str
    selected_root: str
    selected_pattern: str
    rows: list[UnfoldedRow]
    summary_markdown: str

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "selected_root": self.selected_root,
            "selected_pattern": self.selected_pattern,
            "rows": [r.to_dict() for r in self.rows],
            "summary_markdown": self.summary_markdown,
        }

    def to_markdown(self) -> str:
        return self.summary_markdown


class FoldedWordUnfolder:
    """Unfolds a FoldedWordGraph into a human-readable layered representation."""

    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()

    def unfold(self, graph: FoldedWordGraph) -> UnfoldedWordGraph:
        rows: list[UnfoldedRow] = []

        # Root layer
        root = get_root_by_id(graph.selected_root)
        if root:
            rows.append(UnfoldedRow("root", "radicals", "–".join(root.radicals), 1.0))
            rows.append(UnfoldedRow("root", "semantic_core", root.semantic_core, 1.0))
            rows.append(UnfoldedRow("root", "root_type", root.root_type, 1.0))
            rows.append(UnfoldedRow("root", "causation_potential", str(root.causation_potential), root.causation_potential))
        else:
            rows.append(UnfoldedRow("root", "root_id", graph.selected_root, 1.0))

        # Pattern layer
        pattern_op = self._registry.get(graph.selected_pattern)
        if pattern_op:
            rows.append(UnfoldedRow("pattern", "pattern_form", pattern_op.pattern_form, 1.0))
            rows.append(UnfoldedRow("pattern", "family", pattern_op.family, 1.0))
            for k, v in pattern_op.operator_vector.items():
                if v > 0.3:
                    rows.append(UnfoldedRow("pattern", k, f"{v:.2f}", v))

        # Role vector layer
        for role, score in sorted(graph.role_vector.items(), key=lambda x: -x[1]):
            if score > 0.3:
                rows.append(UnfoldedRow("role", role, f"{score:.2f}", score))

        # Domain vector layer
        for domain, score in sorted(graph.domain_vector.items(), key=lambda x: -x[1]):
            if score > 0.3:
                rows.append(UnfoldedRow("domain", domain, f"{score:.2f}", score))

        # Event vector layer
        for ev_key, score in sorted(graph.event_vector.items(), key=lambda x: -x[1]):
            if score > 0.3:
                rows.append(UnfoldedRow("event", ev_key, f"{score:.2f}", score))

        # Build markdown table
        lines = [
            f"# Unfolded Word Graph — {graph.word}",
            "",
            f"**Root:** {graph.selected_root}  |  **Pattern:** {graph.selected_pattern}",
            f"**Certainty Policy:** {graph.certainty_policy}",
            "",
            "| Layer | Key | Value | Score |",
            "|-------|-----|-------|-------|",
        ]
        for r in rows:
            lines.append(f"| {r.layer} | {r.key} | {r.value} | {r.score:.2f} |")

        return UnfoldedWordGraph(
            word=graph.word,
            selected_root=graph.selected_root,
            selected_pattern=graph.selected_pattern,
            rows=rows,
            summary_markdown="\n".join(lines),
        )
