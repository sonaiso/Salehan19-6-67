"""NominativeResolver — distinguishes Arabic nominative roles."""
from __future__ import annotations


class NominativeResolver:
    """Distinguishes nominative roles: فاعل، نائب فاعل، مبتدأ، خبر، اسم كان، خبر إن، تابع مرفوع، مضارع مرفوع."""

    KANA_VERBS = {"كان", "ليس", "صار", "أصبح", "أضحى", "أمسى", "بات", "ظل"}
    INNA_PARTICLES = {"إنّ", "إن", "أنّ", "أن", "كأنّ", "كأن", "لكنّ", "لكن", "ليت", "لعلّ"}

    def resolve(self, surface: str, context_tokens: list, position: int) -> str:
        """Resolve nominative role."""
        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if prev in self.KANA_VERBS:
                return "kana_name"
            if prev in self.INNA_PARTICLES:
                return "inna_predicate"

        if surface.startswith('يَ') or surface.startswith('تَ') or surface.startswith('أَ') or surface.startswith('نَ'):
            return "imperfect_verb_nominative"

        if position == 0:
            return "agent"

        if position == 0 and not self._is_verb(context_tokens[0] if context_tokens else ""):
            return "subject"

        return "agent"

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)

    def _is_verb(self, token: str) -> bool:
        verb_prefixes = ('فَعَ', 'كَتَ', 'ذَهَ', 'جَاءَ', 'قَالَ')
        return any(token.startswith(p) for p in verb_prefixes)
