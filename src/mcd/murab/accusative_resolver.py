"""AccusativeResolver — resolves the specific role of a منصوب token."""
from __future__ import annotations


class AccusativeResolver:
    """Determines the precise syntactic + semantic role of a منصوب token.

    Possible roles:
        مفعول به، مفعول مطلق، مفعول لأجله، مفعول فيه، مفعول معه،
        حال، تمييز، مستثنى، خبر كان، اسم إن، تابع منصوب، فعل مضارع منصوب
    """

    def resolve(
        self,
        surface: str,
        governing_factor_type: str | None,
        position_in_sentence: int,
    ) -> dict:
        warnings: list[str] = []

        if governing_factor_type == "nasib":
            # Particle like لن / أن governing imperfect verb
            return {
                "syntactic_role": "فعل مضارع منصوب",
                "semantic_role": "dependent",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        if governing_factor_type == "nasikh":
            return {
                "syntactic_role": "اسم إن أو خبر كان",
                "semantic_role": "patient",
                "certainty_policy": "certain_syntactic",
                "warnings": ["governing_nasikh_ambiguity_kana_vs_inna"],
            }

        if governing_factor_type == "verb":
            return {
                "syntactic_role": "مفعول به",
                "semantic_role": "patient",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        # Without a clear governing factor, give probable roles
        warnings.append("accusative_role_requires_more_context")
        return {
            "syntactic_role": "مفعول به أو حال أو تمييز",
            "semantic_role": "patient",
            "certainty_policy": "hypothesis",
            "warnings": warnings,
        }
