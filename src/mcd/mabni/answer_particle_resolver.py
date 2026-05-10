"""AnswerParticleResolver — resolves Arabic answer particles."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnswerParticleResult:
    surface: str
    answer_type: str
    reverses_negation: bool
    requires_context: bool
    certainty_policy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "answer_type": self.answer_type,
            "reverses_negation": self.reverses_negation,
            "requires_context": self.requires_context,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }


_ANSWER_PARTICLES: dict[str, tuple[str, bool]] = {
    "نعم": ("affirmative", False),
    "أجل": ("affirmative", False),
    "إي": ("affirmative", False),
    "بلى": ("reversal_affirmative", True),  # reverses prior negation
    "لا": ("negative", False),
    "كلا": ("strong_negative", False),
}


class AnswerParticleResolver:
    """Resolves Arabic answer particles.

    Rules:
    - بلى reverses a prior negation (used after negative question)
    - Answer particles require prior question context
    - Without context, a warning is issued
    """

    def resolve(self, text: str, previous_question: str = "") -> AnswerParticleResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        if not previous_question:
            warnings.append("discourse_context_required: answer particle requires prior question context")

        for token in tokens:
            clean = _strip_diacritics(token)
            if clean in _ANSWER_PARTICLES:
                answer_type, reverses_negation = _ANSWER_PARTICLES[clean]

                if clean == "بلى" and previous_question:
                    # Verify the question was negative
                    if "لم" not in previous_question and "ما" not in previous_question and "لا" not in previous_question:
                        warnings.append(
                            "bala_context_mismatch: بلى is used to reverse negation; "
                            "prior question does not appear to be negative"
                        )

                policy = "standard" if previous_question else "context_pending"

                return AnswerParticleResult(
                    surface=clean,
                    answer_type=answer_type,
                    reverses_negation=reverses_negation,
                    requires_context=True,
                    certainty_policy=policy,
                    warnings=warnings,
                )

        warnings.append("no answer particle found in text")
        return AnswerParticleResult(
            surface="",
            answer_type="none",
            reverses_negation=False,
            requires_context=True,
            certainty_policy="context_pending",
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
