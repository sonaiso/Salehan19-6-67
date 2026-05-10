"""HalTamyizEngine — classifies حال (circumstantial) vs تمييز (specification).

Rule:
    حال تصف هيئة صاحبها (describes the state of a definite referent)
    تمييز يفسر إبهام نسبة أو ذات (disambiguates a vague noun or ratio)
"""
from __future__ import annotations

import re

from mcd.murab.murab_schema import MurabUnit

_HARAKAT = re.compile(r"[\u064b-\u065f]")
_QUANTITY_WORDS = {"كثير", "قليل", "مئة", "ألف", "عشرون", "ثلاثون", "كيلو",
                   "متر", "طن", "أكثر", "أقل"}


class HalTamyizEngine:
    """Classifies accusative tokens as حال, تمييز, or unknown."""

    def classify(
        self,
        surface: str,
        governing_factor_type: str | None,
        context: list[str],
    ) -> dict:
        warnings: list[str] = []
        bare = _HARAKAT.sub("", surface)
        context_bare = [_HARAKAT.sub("", t) for t in context]

        if self._suggests_tamyiz(bare, context_bare):
            return {
                "classification": "tamyiz",
                "relation_type": "nmod:tmod",
                "certainty_policy": "probable_syntactic",
                "warnings": warnings,
            }

        if self._suggests_hal(bare, context_bare, governing_factor_type):
            return {
                "classification": "hal",
                "relation_type": "advcl:manner",
                "certainty_policy": "probable_syntactic",
                "warnings": warnings,
            }

        warnings.append("hal_tamyiz_ambiguous_needs_discourse_context")
        return {
            "classification": "unknown",
            "relation_type": "dep",
            "certainty_policy": "hypothesis",
            "warnings": warnings,
        }

    def _suggests_tamyiz(self, bare: str, context: list[str]) -> bool:
        # If preceded by a quantity word → tamyiz
        return any(q in context for q in _QUANTITY_WORDS)

    def _suggests_hal(
        self,
        bare: str,
        context: list[str],
        gf_type: str | None,
    ) -> bool:
        # Hal usually follows a definite noun or a verb (state of actor)
        return gf_type == "verb"
