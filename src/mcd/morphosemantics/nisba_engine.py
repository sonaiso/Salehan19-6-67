"""NisbaEngine — derives and resolves Arabic nisba (نسبة) adjectives.

The nisba is formed by appending the suffix -iyy (ـيّ) to a noun, creating
a relational adjective meaning "pertaining to X".  This engine handles
derivation, resolution and vector production for nisba forms.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class NisbaResult:
    base_word: str
    nisba_form: str
    nisba_type: str  # simple|truncated|modified|irregular
    relation_domain: str
    operator_vector: dict[str, float]
    certainty: float

    def to_dict(self) -> dict:
        return {
            "base_word": self.base_word,
            "nisba_form": self.nisba_form,
            "nisba_type": self.nisba_type,
            "relation_domain": self.relation_domain,
            "operator_vector": self.operator_vector,
            "certainty": self.certainty,
        }


# Built-in nisba examples
_BUILTIN_NISBA: dict[str, dict] = {
    "عَرَب": {"nisba_form": "عَرَبيّ", "nisba_type": "simple",
              "relation_domain": "ethnicity", "certainty": 1.0},
    "زِراعة": {"nisba_form": "زِراعيّ", "nisba_type": "truncated",
               "relation_domain": "profession", "certainty": 0.9},
    "عِلم": {"nisba_form": "عِلميّ", "nisba_type": "simple",
             "relation_domain": "discipline", "certainty": 1.0},
    "صِناعة": {"nisba_form": "صِناعيّ", "nisba_type": "truncated",
               "relation_domain": "profession", "certainty": 0.9},
    "مَدينة": {"nisba_form": "مَدَنيّ", "nisba_type": "modified",
               "relation_domain": "place", "certainty": 0.85},
    "إسلام": {"nisba_form": "إسلاميّ", "nisba_type": "simple",
              "relation_domain": "religion", "certainty": 1.0},
    "مِصر": {"nisba_form": "مِصريّ", "nisba_type": "simple",
             "relation_domain": "geography", "certainty": 1.0},
    "بَحر": {"nisba_form": "بَحريّ", "nisba_type": "simple",
             "relation_domain": "geography", "certainty": 0.9},
}

_NISBA_OPERATOR_VECTOR = {
    "agency": 0.0, "patienthood": 0.0, "causation": 0.0,
    "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
    "place": 0.0, "instrument": 0.0, "time": 0.0,
    "nisba": 1.0, "diminutive": 0.0, "plurality": 0.0,
    "comparison": 0.0, "mutawaa": 0.0,
}


def _derive_simple_nisba(word: str) -> str:
    """Append -iyy suffix, handling taa marbuta."""
    if word.endswith("ة"):
        return word[:-1] + "يّ"
    return word + "يّ"


class NisbaEngine:
    """Derives and resolves Arabic nisba adjectives."""

    def __init__(self) -> None:
        self._data: dict[str, dict] = dict(_BUILTIN_NISBA)
        self._load()

    def _load(self) -> None:
        path = _DATA_DIR / "nisba_patterns.json"
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data.get("entries", []):
                self._data[entry["base_word"]] = {
                    k: v for k, v in entry.items() if k != "base_word"
                }
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            pass

    def derive(self, base_word: str) -> NisbaResult:
        if base_word in self._data:
            d = self._data[base_word]
            return NisbaResult(
                base_word=base_word,
                nisba_form=d["nisba_form"],
                nisba_type=d["nisba_type"],
                relation_domain=d["relation_domain"],
                operator_vector=dict(_NISBA_OPERATOR_VECTOR),
                certainty=d["certainty"],
            )
        # Fallback: simple derivation
        return NisbaResult(
            base_word=base_word,
            nisba_form=_derive_simple_nisba(base_word),
            nisba_type="simple",
            relation_domain="unknown",
            operator_vector=dict(_NISBA_OPERATOR_VECTOR),
            certainty=0.6,
        )

    def resolve(self, nisba_form: str) -> Optional[str]:
        """Try to find the base word for a given nisba form."""
        for base, d in self._data.items():
            if d["nisba_form"] == nisba_form:
                return base
        return None
