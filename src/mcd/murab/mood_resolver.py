"""MoodResolver — determines the grammatical mood of an Arabic verb."""
from __future__ import annotations

import re

_HARAKAT = re.compile(r"[\u064b-\u065f]")

_NASIB_PARTICLES = {"لن", "أن", "كي", "لكي", "حتى", "إذن"}
_JAZIM_PARTICLES = {"لم", "لمّا", "لام الأمر", "لا الناهية"}


def _strip(text: str) -> str:
    return _HARAKAT.sub("", text)


class MoodResolver:
    """Rule-based verb mood resolver.

    Moods: indicative | subjunctive | jussive | imperative
    """

    def resolve_mood(
        self,
        verb_surface: str,
        governing_factor_type: str | None,
    ) -> str:
        if governing_factor_type == "jazim":
            return "jussive"
        if governing_factor_type == "nasib":
            return "subjunctive"
        # Imperative verbs are identifiable by their morphological pattern
        stripped = _strip(verb_surface)
        if self._looks_imperative(stripped):
            return "imperative"
        return "indicative"

    def _looks_imperative(self, stripped: str) -> bool:
        # Simple heuristic: starts with ا and is short
        return stripped.startswith("ا") and len(stripped) <= 5
