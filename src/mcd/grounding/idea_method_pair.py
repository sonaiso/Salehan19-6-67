"""IdeaMethodPair — extracts idea+method pairs from Arabic text."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Keywords indicating an idea
_IDEA_KEYWORDS = {"نظام", "فكرة", "مبدأ", "هدف", "غاية", "تعليم", "تربية", "نظامًا", "نظاما"}

# Keywords indicating a method
_METHOD_KEYWORDS = {"طريقة", "أسلوب", "منهج", "وسيلة", "أداة", "لـ", "لتربية", "لتعليم", "لتحقيق", "لبناء"}


@dataclass
class IdeaMethodPair:
    idea: str
    method: str
    implementation_path: list[str] = field(default_factory=list)
    carriers: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.5


class IdeaMethodPairModel:
    """Detects and extracts idea-method pairs from Arabic text."""

    def extract(self, text: str) -> Optional[IdeaMethodPair]:
        words = text.strip().split()

        idea_found: list[str] = []
        method_found: list[str] = []

        for i, word in enumerate(words):
            # Check idea keywords
            if any(kw in word for kw in _IDEA_KEYWORDS):
                # Take surrounding context as idea phrase
                start = max(0, i - 1)
                end = min(len(words), i + 3)
                idea_found.append(" ".join(words[start:end]))

            # Check method keywords
            if any(kw in word for kw in _METHOD_KEYWORDS):
                start = max(0, i)
                end = min(len(words), i + 3)
                method_found.append(" ".join(words[start:end]))

        if not idea_found or not method_found:
            return None

        return IdeaMethodPair(
            idea=idea_found[0],
            method=method_found[0],
            certainty=0.5,
        )
