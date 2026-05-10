"""SyntacticRoleResolver — maps (case, context) to syntactic role."""
from __future__ import annotations


class SyntacticRoleResolver:
    """Maps I'rab case and context to syntactic role."""

    NOMINATIVE_ROLES = ["agent", "subject", "predicate", "passive_agent", "kana_name", "inna_predicate", "follower_nom"]
    ACCUSATIVE_ROLES = ["object", "absolute_object", "object_of_purpose", "adverbial", "accompaniment", "hal", "tamyiz", "exception", "kana_predicate", "inna_name"]
    GENITIVE_ROLES = ["object_of_preposition", "mudaf_ilayh", "follower_gen"]
    JUSSIVE_ROLES = ["jussive_verb"]

    def resolve(self, irab_case: str, context: dict = None) -> str:
        """Resolve syntactic role from case and context."""
        context = context or {}

        if irab_case == "nominative":
            if context.get("is_mubtada"):
                return "subject"
            if context.get("is_khabar"):
                return "predicate"
            if context.get("is_kana_name"):
                return "kana_name"
            if context.get("is_inna_khabar"):
                return "inna_predicate"
            return "agent"

        elif irab_case == "accusative":
            if context.get("is_hal"):
                return "hal"
            if context.get("is_tamyiz"):
                return "tamyiz"
            if context.get("is_kana_khabar"):
                return "kana_predicate"
            if context.get("is_inna_name"):
                return "inna_name"
            if context.get("is_exception"):
                return "exception"
            return "object"

        elif irab_case == "genitive":
            if context.get("is_mudaf_ilayh"):
                return "mudaf_ilayh"
            return "object_of_preposition"

        elif irab_case == "jussive":
            return "jussive_verb"

        return "unknown"
