"""SystemDerivation — derives system descriptions from Arabic text."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


_SYSTEM_KEYWORDS = {"نظام", "منظومة", "نظامًا", "نظاما", "منظومةً"}


@dataclass
class SystemDerivation:
    system_name: str
    source_concept: str
    governing_measure: str
    problem_addressed: str
    rules: list[str] = field(default_factory=list)
    procedures: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)
    application_method: str = ""
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.5


class SystemDerivationModel:
    """Detects system keywords and derives a SystemDerivation frame."""

    def derive(self, text: str) -> Optional[SystemDerivation]:
        words = text.strip().split()

        found_keyword: Optional[str] = None
        keyword_index: int = -1

        for i, word in enumerate(words):
            if any(kw in word for kw in _SYSTEM_KEYWORDS):
                found_keyword = word
                keyword_index = i
                break

        if found_keyword is None:
            return None

        # Extract system name from surrounding words
        start = max(0, keyword_index - 1)
        end = min(len(words), keyword_index + 4)
        system_name = " ".join(words[start:end])

        # Source concept is the noun immediately after the system keyword
        source_concept = ""
        if keyword_index + 1 < len(words):
            source_concept = words[keyword_index + 1]

        return SystemDerivation(
            system_name=system_name,
            source_concept=source_concept,
            governing_measure="غير محدد",
            problem_addressed="غير محدد",
            certainty=0.4,
        )
