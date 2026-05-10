"""TraceReport — generates human-readable reports from TraceBundle."""
from __future__ import annotations

import json
from mcd.traceability.trace_builder import TraceBundle
from mcd.traceability.trace_validator import TraceValidator, TraceValidationReport


class TraceReport:
    """Generates reports from a TraceBundle."""

    def __init__(self, bundle: TraceBundle) -> None:
        self.bundle = bundle
        self._validator = TraceValidator()

    def validate(self) -> TraceValidationReport:
        return self._validator.validate(self.bundle)

    def to_markdown(self) -> str:
        b = self.bundle
        vr = self.validate()
        lines = [
            f"# Unicode-to-Cognition Trace Report",
            "",
            f"**Input text:** `{b.text}`",
            "",
            f"## Summary",
            "",
            f"| Layer | Count |",
            f"|-------|-------|",
            f"| Unicode units | {len(b.unicode_units)} |",
            f"| Graphemes | {len(b.graphemes)} |",
            f"| Tokens | {len(b.tokens)} |",
            f"| Node links | {len(b.node_links)} |",
            f"| Edge links | {len(b.edge_links)} |",
            f"| Vector traces | {len(b.vector_traces)} |",
            f"| Evidence traces | {len(b.evidence_traces)} |",
            "",
            f"## Validation",
            "",
            vr.to_markdown(),
            "",
        ]
        if b.judgment_trace:
            jt = b.judgment_trace
            lines += [
                f"## Judgment",
                "",
                f"- **Decision:** `{jt.final_decision}`",
                f"- **Evidence status:** `{jt.evidence_status}`",
                f"- **Certainty policy:** `{jt.certainty_policy}`",
                f"- **Explanation:** {jt.explanation}",
                "",
            ]
            if jt.warnings:
                lines.append("### Warnings")
                for w in jt.warnings:
                    lines.append(f"- {w}")
        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.bundle.to_dict(), ensure_ascii=False, indent=indent)
