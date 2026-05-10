"""EstimatedIrabEngine — handles words whose I'rab marker is not visible.

Cases:
    - مقصور (الفتى): last letter ا or ى → marker estimated
    - منقوص (القاضي): last letter ي in genitive/nominative → marker estimated
    - مضاف إلى ياء المتكلم: ending in ي → marker estimated
"""
from __future__ import annotations

import re

_HARAKAT = re.compile(r"[\u064b-\u065f]")


class EstimatedIrabEngine:
    """Detects whether a word carries an estimated (مقدّر) I'rab marker."""

    def resolve(
        self,
        surface: str,
        irab_case: str,
    ) -> dict:
        bare = _HARAKAT.sub("", surface)
        last = bare[-1] if bare else ""

        # مقصور: ends in ا or ى
        if last in ("ا", "ى"):
            return {
                "has_estimated_marker": True,
                "reason": "maqsur_last_letter_alif_or_alif_maqsura",
                "underlying_marker": self._expected_marker(irab_case),
                "visibility": "estimated",
            }

        # منقوص: ends in ي (in nom or gen — not accusative which shows fatha)
        if last == "ي" and irab_case in ("nominative", "genitive"):
            return {
                "has_estimated_marker": True,
                "reason": "manqus_last_letter_ya",
                "underlying_marker": self._expected_marker(irab_case),
                "visibility": "estimated",
            }

        # مضاف إلى ياء المتكلم: word ends in ي (possessive)
        if bare.endswith("ي") and irab_case == "genitive":
            return {
                "has_estimated_marker": True,
                "reason": "mudaf_ila_ya_mutakallim",
                "underlying_marker": "kasra",
                "visibility": "estimated",
            }

        return {
            "has_estimated_marker": False,
            "reason": "marker_visible",
            "underlying_marker": self._expected_marker(irab_case),
            "visibility": "apparent",
        }

    def _expected_marker(self, irab_case: str) -> str:
        return {
            "nominative": "damma",
            "accusative": "fatha",
            "genitive": "kasra",
            "jussive": "sukun",
        }.get(irab_case, "none")
