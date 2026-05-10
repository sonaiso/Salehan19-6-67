"""MabniTraceLinker — links Unicode tokens through the Mabni analysis chain."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MabniTraceLink:
    unicode_token: str
    token_idx: int
    operator_id: str
    graph_node_id: str
    evidence_link: str
    certainty_effect: str
    judgment_status: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "unicode_token": self.unicode_token,
            "token_idx": self.token_idx,
            "operator_id": self.operator_id,
            "graph_node_id": self.graph_node_id,
            "evidence_link": self.evidence_link,
            "certainty_effect": self.certainty_effect,
            "judgment_status": self.judgment_status,
            "warnings": self.warnings,
        }


@dataclass
class MabniTraceReport:
    links: list[MabniTraceLink] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"links": [lnk.to_dict() for lnk in self.links]}


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)


class MabniTraceLinker:
    """Links Unicode tokens through the Mabni analysis chain.

    For each token in the input text, produces a trace link containing:
      Unicode → Token → Operator → Graph Node → Evidence → Certainty → Judgment
    """

    def link(self, text: str, unfold_result: dict[str, Any], graph: Any | None = None) -> MabniTraceReport:
        tokens = text.split()
        links: list[MabniTraceLink] = []

        for idx, token in enumerate(tokens):
            clean = _strip_diacritics(token)

            # Find matching operator result
            operator_id = ""
            certainty_effect = "none"
            judgment_status = "unknown"
            evidence_link = "no_direct_evidence"
            warnings: list[str] = []
            graph_node_id = ""

            for key, value in unfold_result.items():
                if not isinstance(value, dict):
                    continue
                surface = _strip_diacritics(value.get("surface", ""))
                if not surface:
                    continue
                if surface == clean or clean.startswith(surface) or surface.startswith(clean):
                    operator_id = value.get("operator_id", key)
                    certainty_effect = str(value.get("certainty_effect", value.get("certainty_note", "none")))
                    is_evidence = value.get("is_evidence", value.get("creates_evidence", False))
                    evidence_link = "direct" if is_evidence else "no_direct_evidence"
                    if value.get("judgment_suspended", False):
                        judgment_status = "suspended"
                    elif "answer_type" in value:
                        judgment_status = "context_dependent"
                    else:
                        judgment_status = "applicable"
                    break

            # Try to resolve graph node ID
            if graph is not None:
                for node in getattr(graph, "nodes", []):
                    if _strip_diacritics(node.surface) == clean or node.operator_id == operator_id:
                        graph_node_id = node.node_id
                        break

            if not operator_id:
                warnings.append(f"token_unmatched: no mabni operator matched token '{token}'")
                judgment_status = "not_analyzed"

            links.append(
                MabniTraceLink(
                    unicode_token=token,
                    token_idx=idx,
                    operator_id=operator_id,
                    graph_node_id=graph_node_id,
                    evidence_link=evidence_link,
                    certainty_effect=certainty_effect,
                    judgment_status=judgment_status,
                    warnings=warnings,
                )
            )

        return MabniTraceReport(links=links)
