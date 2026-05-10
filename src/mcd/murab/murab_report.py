"""MurabReport — generates reports from MurabUnit list."""
from __future__ import annotations
import json
from mcd.murab.murab_schema import MurabUnit


class MurabReport:
    """Generates markdown/text/json report from list of MurabUnit."""

    def __init__(self, units: list):
        self.units = units

    def to_json(self) -> str:
        return json.dumps([u.to_dict() for u in self.units], ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        lines = ["# Arabic I'rab (Mu'rab) Analysis\n"]
        lines.append("| # | Surface | Case | Marker | Visibility | Syntactic Role | Semantic Role | Certainty |")
        lines.append("|---|---------|------|--------|------------|----------------|---------------|-----------|")

        for i, unit in enumerate(self.units, 1):
            lines.append(
                f"| {i} | {unit.surface} | {unit.irab_case} | {unit.irab_marker} | "
                f"{unit.marker_visibility} | {unit.syntactic_role} | {unit.semantic_role} | {unit.certainty_policy} |"
            )

        lines.append("")
        lines.append("## Warnings")
        for unit in self.units:
            if unit.warnings:
                lines.append(f"- **{unit.surface}**: {', '.join(unit.warnings)}")

        return "\n".join(lines)

    def to_text(self) -> str:
        lines = ["Arabic I'rab Analysis", "=" * 40]

        for unit in self.units:
            lines.append(f"\nToken: {unit.surface}")
            lines.append(f"  Case: {unit.irab_case}")
            lines.append(f"  Marker: {unit.irab_marker} ({unit.marker_visibility})")
            lines.append(f"  Syntactic Role: {unit.syntactic_role}")
            lines.append(f"  Semantic Role: {unit.semantic_role}")
            lines.append(f"  Certainty: {unit.certainty_policy}")
            if unit.warnings:
                lines.append(f"  Warnings: {', '.join(unit.warnings)}")

        return "\n".join(lines)
