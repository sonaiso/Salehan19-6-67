"""CaseResolver — heuristic I'rab case detection from harakat and context."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from mcd.murab.governing_factor import GoverningFactor, GOVERNING_FACTOR_REGISTRY

# Arabic diacritic code points
_DAMMA         = "\u064f"   # ُ  damma (nominative)
_FATHA         = "\u064e"   # َ  fatha (accusative)
_KASRA         = "\u0650"   # ِ  kasra (genitive)
_SUKUN         = "\u0652"   # ْ  sukun (jussive)
_SHADDA        = "\u0651"   # ّ  shadda
_TANWIN_DAMMA  = "\u064c"   # ٌ  tanwin damma (nominative, nunation)
_TANWIN_FATHA  = "\u064b"   # ً  tanwin fatha (accusative, nunation)
_TANWIN_KASRA  = "\u064d"   # ٍ  tanwin kasra (genitive, nunation)

# Harakat strip pattern
_HARAKAT = re.compile(r"[\u064b-\u065f]")

# Map any haraka to its base case and marker name
_HARAKA_TO_CASE: dict[str, tuple[str, str]] = {
    _DAMMA:        ("nominative", "damma"),
    _TANWIN_DAMMA: ("nominative", "damma"),
    _FATHA:        ("accusative", "fatha"),
    _TANWIN_FATHA: ("accusative", "fatha"),
    _KASRA:        ("genitive",   "kasra"),
    _TANWIN_KASRA: ("genitive",   "kasra"),
    _SUKUN:        ("jussive",    "sukun"),
}


def _strip_harakat(text: str) -> str:
    return _HARAKAT.sub("", text)


def _last_haraka(surface: str) -> Optional[str]:
    """Return the final case-bearing diacritic on the surface form."""
    for ch in reversed(surface):
        if ch in _HARAKA_TO_CASE:
            return ch
    return None


class CaseResolver:
    """Rule-based I'rab case resolver using harakat and governing factors."""

    def resolve(
        self,
        surface: str,
        context_tokens: list[str],
    ) -> tuple[str, str, Optional[str], str, list[str]]:
        """Resolve I'rab for *surface* given surrounding *context_tokens*.

        Returns
        -------
        (irab_case, irab_marker, governing_factor_id, certainty_policy, warnings)
        """
        warnings: list[str] = []
        governing_factor_id: Optional[str] = None

        # 1. Detect governing factor from immediately preceding context token
        gf = self._find_governing_factor(context_tokens)
        if gf:
            governing_factor_id = gf.factor_id

        # 2. Detect last haraka in surface
        last = _last_haraka(surface)

        # 3. Determine case from haraka (overrides gf when explicit)
        if last and last in _HARAKA_TO_CASE:
            irab_case, irab_marker = _HARAKA_TO_CASE[last]
            return (irab_case, irab_marker, governing_factor_id, "certain_syntactic", warnings)

        # 4. No haraka visible — fall back to governing factor inference
        if gf:
            if "genitive" in gf.governs_case:
                warnings.append("marker_not_visible_estimated_from_governing_factor")
                return ("genitive", "estimated", governing_factor_id, "probable_syntactic", warnings)
            if "jussive" in gf.governs_case:
                warnings.append("marker_not_visible_estimated_from_governing_factor")
                return ("jussive", "estimated", governing_factor_id, "probable_syntactic", warnings)
            if "accusative" in gf.governs_case and "nominative" not in gf.governs_case:
                warnings.append("marker_not_visible_estimated_from_governing_factor")
                return ("accusative", "estimated", governing_factor_id, "probable_syntactic", warnings)

        # 5. Completely unknown
        warnings.append("no_haraka_no_governing_factor_found")
        return ("unknown", "none", governing_factor_id, "hypothesis", warnings)

    def _find_governing_factor(
        self, context_tokens: list[str]
    ) -> Optional[GoverningFactor]:
        """Search recent context for a known governing factor."""
        # Check the immediately preceding tokens (up to 3)
        for tok in reversed(context_tokens[-3:]):
            stripped = _strip_harakat(tok)
            gf = GOVERNING_FACTOR_REGISTRY.get_by_surface(stripped)
            if gf:
                return gf
            # Check with ب prefix attached (e.g., بالقلم)
            if stripped.startswith("ب"):
                gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("ب")
                if gf:
                    return gf
        return None
