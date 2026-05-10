"""AccusativeResolver — distinguishes Arabic accusative roles."""
from __future__ import annotations


class AccusativeResolver:
    """Distinguishes accusative roles: مفعول به، مفعول مطلق، مفعول لأجله، مفعول فيه، مفعول معه، حال، تمييز، مستثنى، خبر كان، اسم إن."""

    HAL_PATTERNS = {"حَالٌ", "ماشياً", "راكباً", "فرحاً", "حزيناً"}
    TAMYIZ_PATTERNS = {"كيلوغراماً", "متراً", "عاماً", "رطلاً"}
    EXCEPTION_MARKERS = {"إلّا", "إلا", "غير", "سوى"}
    INNA_PARTICLES = {"إنّ", "إن", "أنّ", "أن", "كأنّ", "كأن", "لكنّ", "لكن", "ليت", "لعلّ"}
    KANA_VERBS = {"كان", "ليس", "صار", "أصبح", "أضحى", "أمسى", "بات", "ظل"}

    def resolve(self, surface: str, context_tokens: list, position: int) -> str:
        """Resolve accusative role."""
        stripped = self._strip_diacritics(surface)

        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if prev in self.EXCEPTION_MARKERS or prev in {"إلّا", "إلا"}:
                return "exception"

            if prev in self.INNA_PARTICLES:
                return "inna_name"

            if position >= 2:
                prev2 = self._strip_diacritics(context_tokens[position - 2])
                if prev2 in self.KANA_VERBS:
                    return "kana_predicate"

        if self._looks_like_hal(surface, stripped):
            return "hal"

        if self._looks_like_tamyiz(surface, stripped):
            return "tamyiz"

        return "object"

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)

    def _looks_like_hal(self, surface: str, stripped: str) -> bool:
        return surface.endswith('\u064b') and len(stripped) > 5

    def _looks_like_tamyiz(self, surface: str, stripped: str) -> bool:
        return surface.endswith('\u064b') and len(stripped) <= 5
