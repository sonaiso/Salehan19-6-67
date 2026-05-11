"""SyntacticRoleResolver — derives role from case + position + governing factor."""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit
from mcd.murab.governing_factor import GOVERNING_FACTOR_REGISTRY


class SyntacticRoleResolver:
    """Maps (irab_case, governing_factor_type, position) → syntactic role."""

    def resolve(self, murab_unit: MurabUnit, sentence_units: list[MurabUnit]) -> str:
        case = murab_unit.irab_case
        gf_id = murab_unit.governing_factor_id
        gf = GOVERNING_FACTOR_REGISTRY.get(gf_id) if gf_id else None
        gf_type = gf.factor_type if gf else None
        position = self._position_in_sentence(murab_unit, sentence_units)
        word_type = murab_unit.word_type

        if word_type in ("verb",):
            return "فعل"

        if case == "nominative":
            return self._resolve_nominative(gf_type, position, sentence_units, murab_unit)

        if case == "accusative":
            return self._resolve_accusative(gf_type, position)

        if case == "genitive":
            return self._resolve_genitive(gf_type)

        if case == "jussive":
            return "فعل مضارع مجزوم"

        if case == "indeclinable_local":
            return "مبني"

        return "غير محدد"

    # ------------------------------------------------------------------ #
    def _resolve_nominative(
        self,
        gf_type: str | None,
        position: int,
        sentence_units: list[MurabUnit],
        unit: MurabUnit,
    ) -> str:
        # After a past verb or agent verb → فاعل
        preceding_verb = self._preceding_verb(unit, sentence_units)
        if preceding_verb:
            return "فاعل"
        if gf_type == "nasikh":
            return "اسم كان أو خبر إن"
        if position == 0:
            return "مبتدأ"
        return "خبر"

    def _resolve_accusative(self, gf_type: str | None, position: int) -> str:
        if gf_type == "nasikh":
            return "خبر كان أو اسم إن"
        if gf_type == "verb":
            return "مفعول به"
        return "مفعول به"

    def _resolve_genitive(self, gf_type: str | None) -> str:
        if gf_type == "preposition":
            return "اسم مجرور بحرف جر"
        return "مضاف إليه"

    def _position_in_sentence(
        self, unit: MurabUnit, sentence_units: list[MurabUnit]
    ) -> int:
        for i, u in enumerate(sentence_units):
            if u.unit_id == unit.unit_id:
                return i
        return 0

    def _preceding_verb(
        self, unit: MurabUnit, sentence_units: list[MurabUnit]
    ) -> MurabUnit | None:
        pos = self._position_in_sentence(unit, sentence_units)
        for i in range(pos - 1, -1, -1):
            u = sentence_units[i]
            if u.word_type in ("verb", "imperfect_verb"):
                return u
        return None
