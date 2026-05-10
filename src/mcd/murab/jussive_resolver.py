"""JussiveResolver — resolves the specific role of a مجزوم imperfect verb."""
from __future__ import annotations


class JussiveResolver:
    """Resolves syntactic role of a جازم-governed imperfect verb.

    Roles: فعل مضارع مجزوم، فعل شرط، جواب شرط
    Only applies to imperfect (مضارع) verbs.
    """

    _CONDITIONAL_PARTICLES = {"إن", "إذا", "من", "ما", "مهما", "كيفما", "أينما",
                               "متى", "أيان", "أنّى", "حيثما", "أي"}

    def resolve(
        self,
        surface: str,
        governing_factor_type: str | None,
    ) -> dict:
        warnings: list[str] = []

        if governing_factor_type == "jazim":
            return {
                "syntactic_role": "فعل مضارع مجزوم",
                "semantic_role": "dependent",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        # Conditional context heuristic
        warnings.append("jussive_governing_factor_not_found_heuristic_applied")
        return {
            "syntactic_role": "فعل شرط أو جواب شرط",
            "semantic_role": "dependent",
            "certainty_policy": "hypothesis",
            "warnings": warnings,
        }
