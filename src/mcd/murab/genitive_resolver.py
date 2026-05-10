"""GenitiveResolver — resolves the specific role of a مجرور token."""
from __future__ import annotations


class GenitiveResolver:
    """Determines the precise syntactic + semantic role of a مجرور token.

    Possible roles:
        اسم مجرور بحرف جر، مضاف إليه، تابع مجرور
    """

    def resolve(
        self,
        surface: str,
        governing_factor_type: str | None,
    ) -> dict:
        warnings: list[str] = []

        if governing_factor_type == "preposition":
            return {
                "syntactic_role": "اسم مجرور بحرف جر",
                "semantic_role": "possessed",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        if governing_factor_type == "idafa":
            return {
                "syntactic_role": "مضاف إليه",
                "semantic_role": "possessor",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        # Default: إضافة (genitive by construction)
        warnings.append("genitive_governing_factor_not_identified_assuming_idafa")
        return {
            "syntactic_role": "مضاف إليه أو تابع مجرور",
            "semantic_role": "possessor",
            "certainty_policy": "probable_syntactic",
            "warnings": warnings,
        }
