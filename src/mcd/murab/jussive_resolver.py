"""JussiveResolver — detects Arabic jussive mood."""
from __future__ import annotations


class JussiveResolver:
    """Detects jussive (جزم) from لم، لا الناهية، إن الشرطية، لما."""

    JUSSIVE_PARTICLES = {"لم", "لما", "لا"}
    CONDITIONAL_PARTICLES = {"إن", "إنْ", "مَن", "ما", "مهما", "متى", "أيّ", "أين", "أينما"}

    def resolve(self, surface: str, context_tokens: list, position: int) -> dict:
        """Resolve jussive details."""
        governing = None
        jussive_type = "unknown"

        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if prev == "لم":
                governing = "لم"
                jussive_type = "negation_past"
            elif prev == "لما":
                governing = "لما"
                jussive_type = "negation_still"
            elif prev == "لا":
                governing = "لا"
                jussive_type = "prohibition"
            elif prev in self.CONDITIONAL_PARTICLES:
                governing = prev
                jussive_type = "conditional_answer"

        return {
            "syntactic_role": "jussive_verb",
            "governing": governing,
            "jussive_type": jussive_type,
        }

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
