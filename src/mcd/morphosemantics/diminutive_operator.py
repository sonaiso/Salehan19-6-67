"""DiminutiveOperator — derives Arabic diminutive (تصغير) forms.

The Arabic diminutive pattern فُعَيِّل conveys smallness, endearment, or
contempt.  This module derives diminutive forms from roots and handles
common phonological adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiminutiveResult:
    base_word: str
    diminutive_form: str
    pattern: str  # fuayyil|fuayyyal|mufayyil
    semantic_shade: str  # smallness|endearment|contempt|approximation
    certainty: float
    operator_vector: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "base_word": self.base_word,
            "diminutive_form": self.diminutive_form,
            "pattern": self.pattern,
            "semantic_shade": self.semantic_shade,
            "certainty": self.certainty,
            "operator_vector": self.operator_vector,
        }


_DIM_VECTOR = {
    "agency": 0.0, "patienthood": 0.0, "causation": 0.0,
    "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
    "place": 0.0, "instrument": 0.0, "time": 0.0,
    "nisba": 0.0, "diminutive": 1.0, "plurality": 0.0,
    "comparison": 0.0, "mutawaa": 0.0,
}

# Known irregular/special diminutives
_KNOWN: dict[str, dict] = {
    "كِتاب": {"diminutive_form": "كُتَيِّب", "pattern": "فُعَيِّل",
              "semantic_shade": "smallness", "certainty": 1.0},
    "بَيت": {"diminutive_form": "بُيَيِّت", "pattern": "فُعَيِّل",
             "semantic_shade": "endearment", "certainty": 1.0},
    "رَجُل": {"diminutive_form": "رُجَيِّل", "pattern": "فُعَيِّل",
              "semantic_shade": "contempt", "certainty": 0.9},
    "كَلب": {"diminutive_form": "كُلَيِّب", "pattern": "فُعَيِّل",
             "semantic_shade": "contempt", "certainty": 0.9},
    "نَهر": {"diminutive_form": "نُهَيِّر", "pattern": "فُعَيِّل",
             "semantic_shade": "smallness", "certainty": 0.9},
    "جَبَل": {"diminutive_form": "جُبَيِّل", "pattern": "فُعَيِّل",
              "semantic_shade": "smallness", "certainty": 0.9},
}


def _default_diminutive(word: str) -> str:
    """Attempt a naive triliteral diminutive: فُعَيِّل pattern."""
    # Strip taa marbuta if present
    if word.endswith("ة"):
        word = word[:-1]
    letters = [c for c in word if '\u0600' <= c <= '\u06ff' and c not in '\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652']
    if len(letters) >= 3:
        return letters[0] + "ُ" + letters[1] + "َيِّ" + letters[2]
    return word + "ُيَيِّل"


class DiminutiveOperator:
    """Derives diminutive forms from Arabic base words."""

    def derive(self, base_word: str, semantic_shade: str = "smallness") -> DiminutiveResult:
        if base_word in _KNOWN:
            d = _KNOWN[base_word]
            return DiminutiveResult(
                base_word=base_word,
                diminutive_form=d["diminutive_form"],
                pattern=d["pattern"],
                semantic_shade=d.get("semantic_shade", semantic_shade),
                certainty=d["certainty"],
                operator_vector=dict(_DIM_VECTOR),
            )
        return DiminutiveResult(
            base_word=base_word,
            diminutive_form=_default_diminutive(base_word),
            pattern="فُعَيِّل",
            semantic_shade=semantic_shade,
            certainty=0.6,
            operator_vector=dict(_DIM_VECTOR),
        )
