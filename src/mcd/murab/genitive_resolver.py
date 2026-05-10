"""GenitiveResolver — distinguishes Arabic genitive roles."""
from __future__ import annotations


class GenitiveResolver:
    """Distinguishes genitive roles: مجرور بحرف جر، مضاف إليه، تابع مجرور."""

    PREPOSITIONS = {"في", "من", "إلى", "على", "عن", "ب", "ل", "ك", "منذ", "مذ", "حتى"}

    def resolve(self, surface: str, context_tokens: list, position: int) -> str:
        """Resolve genitive role."""
        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if prev in self.PREPOSITIONS:
                return "object_of_preposition"

        return "mudaf_ilayh"

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
