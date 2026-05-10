"""MurabCertaintyPolicy — computes certainty for I'rab analysis."""
from __future__ import annotations
from mcd.murab.murab_schema import MurabUnit


class MurabCertaintyPolicy:
    """
    Certainty rules:
    - apparent marker + clear governing factor → syntactic_certainty=0.9
    - estimated marker + clear factor → syntactic_certainty=0.7
    - unclear factor → syntactic_certainty=0.5, warning="hypothesis"
    - multiple valid i'rab → syntactic_certainty=0.4, warning="ambiguous"
    - evidence_effect = "syntactic_only" always
    """

    def evaluate(self, unit: MurabUnit) -> dict:
        """Evaluate certainty policy for a MurabUnit."""
        warnings = list(unit.warnings)

        apparent = unit.marker_visibility == "apparent"
        has_factor = unit.governing_factor_id is not None

        if unit.irab_case == "unknown":
            syntactic_certainty = 0.4
            if "ambiguous" not in warnings:
                warnings.append("ambiguous")
        elif apparent and has_factor:
            syntactic_certainty = 0.9
        elif apparent and not has_factor:
            syntactic_certainty = 0.75
        elif not apparent and has_factor:
            syntactic_certainty = 0.7
            if "hypothesis" not in warnings:
                warnings.append("estimated_marker")
        else:
            syntactic_certainty = 0.5
            if "hypothesis" not in warnings:
                warnings.append("hypothesis")

        semantic_certainty = syntactic_certainty * 0.8

        return {
            "syntactic_certainty": syntactic_certainty,
            "semantic_certainty": semantic_certainty,
            "evidence_effect": "syntactic_only",
            "warnings": warnings,
        }
