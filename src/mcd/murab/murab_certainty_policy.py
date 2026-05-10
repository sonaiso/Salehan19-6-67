"""MurabCertaintyPolicy — evaluates syntactic vs. factual certainty.

Key principle:
    syntactic_certainty ≠ factual_certainty
    I'rab raises syntactic confidence ONLY (evidence_effect = "syntactic_only")
"""
from __future__ import annotations

from typing import Optional

from mcd.murab.murab_schema import MurabUnit
from mcd.murab.governing_factor import GoverningFactor


class MurabCertaintyPolicy:
    """Evaluates the certainty level of an I'rab analysis."""

    def evaluate(
        self,
        murab_unit: MurabUnit,
        governing_factor: Optional[GoverningFactor],
    ) -> dict:
        warnings: list[str] = []

        marker_visible = murab_unit.marker_visibility == "apparent"
        gf_clear = governing_factor is not None and governing_factor.certainty >= 0.9

        # Determine syntactic certainty
        if marker_visible and gf_clear:
            syntactic_certainty = "certain_syntactic"
        elif murab_unit.marker_visibility in ("estimated", "local") and gf_clear:
            syntactic_certainty = "probable_syntactic"
        elif not gf_clear and marker_visible:
            syntactic_certainty = "probable_syntactic"
            warnings.append("governing_factor_unclear_or_missing")
        else:
            syntactic_certainty = "hypothesis"
            warnings.append("both_marker_and_governing_factor_uncertain")

        # Check for multiple irab possibilities (ambiguity)
        if murab_unit.irab_case == "unknown":
            warnings.append("ambiguity_warning: irab_case_could_not_be_determined")

        # I'rab raises syntactic certainty ONLY — not factual certainty
        return {
            "syntactic_certainty": syntactic_certainty,
            "semantic_certainty": "not_evaluated",  # separate domain
            "evidence_effect": "syntactic_only",
            "governing_factor_id": governing_factor.factor_id if governing_factor else None,
            "warnings": warnings,
        }
