"""MurabTraceLinker — creates trace chain from MurabUnit."""
from __future__ import annotations
from mcd.murab.murab_schema import MurabUnit


class MurabTraceLinker:
    """Creates a trace chain: UnicodeTrace → TokenTrace → MurabUnit → I'rabCase → GoverningFactor → SyntacticRole → SemanticRole."""

    def link(self, unit: MurabUnit) -> dict:
        """Create trace chain for a MurabUnit."""
        return {
            "surface": unit.surface,
            "unicode_trace": self._unicode_trace(unit.surface),
            "token_trace": unit.token_id,
            "murab_unit_id": unit.unit_id,
            "irab_case": unit.irab_case,
            "irab_marker": unit.irab_marker,
            "marker_visibility": unit.marker_visibility,
            "governing_factor": unit.governing_factor_id,
            "syntactic_role": unit.syntactic_role,
            "semantic_role": unit.semantic_role,
            "certainty_policy": unit.certainty_policy,
            "warnings": unit.warnings,
            "trace_chain": [
                unit.surface,
                unit.token_id,
                unit.unit_id,
                unit.irab_case,
                unit.governing_factor_id or "none",
                unit.syntactic_role,
                unit.semantic_role,
            ],
        }

    def _unicode_trace(self, surface: str) -> list:
        """Return Unicode codepoints for each character."""
        return [f"U+{ord(c):04X}" for c in surface]
