"""PublicOpinionModel — models public opinion frames from Arabic text."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


_REJECTION_WORDS = {"يرفض", "رفض", "يعارض", "معارضة", "يكره"}
_ACCEPTANCE_WORDS = {"يقبل", "قبول", "يؤيد", "تأييد", "يحب"}
_CORRUPTION_WORDS = {"الفساد", "فساد", "الظلم", "الكذب", "الغش"}


@dataclass
class PublicOpinionFrame:
    idea: str
    emotion: str
    social_spread: float
    supporting_systems: list[str] = field(default_factory=list)
    opposing_systems: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.2
    warnings: list[str] = field(default_factory=list)


class PublicOpinionModel:
    """Extracts public opinion frames from text."""

    def analyze(self, text: str) -> PublicOpinionFrame:
        words = text.strip().split()
        emotion = ""
        idea_parts: list[str] = []

        for word in words:
            if any(w in word for w in _REJECTION_WORDS):
                emotion = "رفض"
            elif any(w in word for w in _ACCEPTANCE_WORDS):
                emotion = "قبول"

            if any(w in word for w in _CORRUPTION_WORDS):
                idea_parts.append(word)

        # If no specific idea found, use the whole text
        if not idea_parts:
            # Extract content after the emotion word
            idea = text.strip()
            for w in _REJECTION_WORDS | _ACCEPTANCE_WORDS:
                idea = idea.replace(w, "").strip()
            idea = idea.strip()
        else:
            idea = " ".join(idea_parts)
        if emotion:
            idea = f"{emotion} {idea}".strip()

        frame = PublicOpinionFrame(
            idea=idea,
            emotion=emotion,
            social_spread=0.3,
            certainty=0.2,
        )

        # If no supporting systems and no evidence → warn and keep certainty low
        if not frame.supporting_systems and not frame.evidence:
            frame.warnings.append("no_systemic_support")
            # certainty stays at 0.2 (default)

        return frame
