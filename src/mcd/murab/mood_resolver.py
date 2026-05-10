"""MoodResolver — detects mood of Arabic imperfect verbs."""
from __future__ import annotations


class MoodResolver:
    """Detects mood of imperfect verb: مرفوع/منصوب/مجزوم."""

    JUSSIVE_PARTICLES = {"لم", "لما", "لا", "لام الأمر", "لا الناهية"}
    NASB_PARTICLES = {"لن", "أن", "كي", "إذن", "حتى", "لام كي", "فاء السببية"}

    def resolve(self, surface: str, context_tokens: list, position: int) -> str:
        """Resolve imperfect verb mood."""
        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if prev in self.JUSSIVE_PARTICLES:
                return "jussive"
            if prev in self.NASB_PARTICLES:
                return "accusative_mood"
        return "nominative_mood"

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
