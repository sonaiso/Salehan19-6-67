"""NominativeResolver — resolves the specific role of a nominative (مرفوع) word."""
from __future__ import annotations


_KANA_SISTERS = {"كان", "أصبح", "أمسى", "أضحى", "ظل", "بات", "صار", "ليس",
                 "مازال", "مادام", "مابرح", "مانفك"}
_INNA_SISTERS = {"إنّ", "أنّ", "كأنّ", "لكنّ", "ليت", "لعلّ"}


class NominativeResolver:
    """Determines the precise syntactic + semantic role of a مرفوع token.

    Rule: not every nominative is فاعل — position and governing factor matter.
    Example: جاء زيدٌ → زيد فاعل مرفوع
    """

    def resolve(
        self,
        surface: str,
        governing_factor_type: str | None,
        position_in_sentence: int,
    ) -> dict:
        warnings: list[str] = []

        if governing_factor_type == "verb":
            return {
                "syntactic_role": "فاعل",
                "semantic_role": "agent",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        if governing_factor_type == "nasikh":
            # Could be اسم كان or خبر إن depending on surface matching
            return {
                "syntactic_role": "اسم ناسخ (اسم كان / خبر إن)",
                "semantic_role": "subject",
                "certainty_policy": "certain_syntactic",
                "warnings": ["governing_nasikh_ambiguity_between_kana_and_inna"],
            }

        if position_in_sentence == 0:
            return {
                "syntactic_role": "مبتدأ",
                "semantic_role": "subject",
                "certainty_policy": "probable_syntactic",
                "warnings": warnings,
            }

        if position_in_sentence > 0:
            # Could be خبر, تابع مرفوع, نائب فاعل, فعل مضارع مرفوع
            warnings.append("nominative_role_requires_more_context")
            return {
                "syntactic_role": "خبر أو تابع مرفوع",
                "semantic_role": "predicate",
                "certainty_policy": "hypothesis",
                "warnings": warnings,
            }

        warnings.append("nominative_role_undetermined")
        return {
            "syntactic_role": "غير محدد",
            "semantic_role": "unknown",
            "certainty_policy": "hypothesis",
            "warnings": warnings,
        }
