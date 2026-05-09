"""SocietyModel — models societal concepts from Arabic text."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


_SOCIETY_KEYWORDS = {"المجتمع", "مجتمع", "الناس", "الجماعة", "العامة", "الشعب"}
_INDIVIDUAL_KEYWORDS = {"شخص", "فرد", "شخصًا", "أنا", "هو", "هي"}
_IDEA_KEYWORDS = {"فكرة", "رأي", "نظرية", "مبدأ"}
_FEELING_KEYWORDS = {"يرفض", "يقبل", "يحب", "يكره", "يؤيد", "يعارض", "رفض", "قبول"}
_SYSTEM_KEYWORDS = {"نظام", "قانون", "مؤسسة", "حكومة"}


@dataclass
class SocietyFrame:
    individuals: list[str] = field(default_factory=list)
    ideas: list[str] = field(default_factory=list)
    public_feelings: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    dominant_measures: list[str] = field(default_factory=list)
    public_opinion: Optional[str] = None
    civilizational_basis: str = ""
    certainty: float = 0.3
    warnings: list[str] = field(default_factory=list)


class SocietyModel:
    """Analyzes text for societal concepts."""

    def analyze(self, text: str) -> SocietyFrame:
        words = text.strip().split()
        frame = SocietyFrame()

        has_society_ref = False
        has_individual_only = False
        has_ideas = False
        has_feelings = False
        has_systems = False

        for word in words:
            if any(kw in word for kw in _SOCIETY_KEYWORDS):
                has_society_ref = True

            if any(kw in word for kw in _INDIVIDUAL_KEYWORDS):
                frame.individuals.append(word)
                has_individual_only = True

            if any(kw in word for kw in _IDEA_KEYWORDS):
                frame.ideas.append(word)
                has_ideas = True

            if any(kw in word for kw in _FEELING_KEYWORDS):
                frame.public_feelings.append(word)
                has_feelings = True

            if any(kw in word for kw in _SYSTEM_KEYWORDS):
                frame.systems.append(word)
                has_systems = True

        # A group of individuals is NOT a society without ideas + feelings + systems
        if has_society_ref:
            if not has_ideas:
                frame.warnings.append("missing_ideas_in_society")
                frame.certainty -= 0.05

            if not has_feelings:
                frame.warnings.append("missing_feelings_in_society")
                frame.certainty -= 0.05

            if not has_systems:
                frame.warnings.append("missing_systems_in_society")
                frame.certainty -= 0.05

            # Extract public opinion phrase
            frame.public_opinion = text.strip()

        # Warn: single individual's statement is not public opinion
        if has_individual_only and not has_society_ref:
            frame.warnings.append("individual_statement_not_public_opinion")
            frame.certainty = max(0.05, frame.certainty - 0.15)

        frame.certainty = max(0.0, min(1.0, frame.certainty))
        return frame
