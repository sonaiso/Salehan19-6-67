"""TawabiEngine — resolves تابع (following word) which inherits its antecedent's case.

Rule: تابع يرث إعراب المتبوع
"""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit


class TawabiEngine:
    """Resolves the type of تابع and inherits I'rab from المتبوع.

    tabi_types: naat | atf | tawkid | badal | atf_bayan
    """

    _ATAF_PARTICLES = {"و", "ف", "ثم", "أو", "أم", "بل", "لكن", "لا"}

    def resolve(
        self,
        matboo: MurabUnit,
        tabi: MurabUnit,
        context: list[str],
    ) -> dict:
        warnings: list[str] = []
        tabi_type = self._classify_tabi(context)

        inherited_case = matboo.irab_case
        inherited_marker = matboo.irab_marker

        if tabi.irab_case != inherited_case and tabi.irab_case != "unknown":
            warnings.append(
                f"tabi_case_mismatch: expected {inherited_case} "
                f"got {tabi.irab_case}"
            )

        return {
            "tabi_type": tabi_type,
            "inherited_case": inherited_case,
            "inherited_marker": inherited_marker,
            "matboo_id": matboo.unit_id,
            "tabi_id": tabi.unit_id,
            "relation": f"tabi_{tabi_type}",
            "warnings": warnings,
        }

    def _classify_tabi(self, context: list[str]) -> str:
        import re
        _H = re.compile(r"[\u064b-\u065f]")
        for tok in context:
            bare = _H.sub("", tok)
            if bare in self._ATAF_PARTICLES:
                return "atf"
        # Default: naat (adjective following noun)
        return "naat"
