"""PatternOperatorRegistry — Arabic morphological patterns as cognitive operators.

A pattern (وزن) is not merely a phonological template: it is a *cognitive
operator* that projects a root's potential into a specific semantic role
(agent, patient, place, event, attribute, etc.).  The registry maps pattern
forms to their operator vectors so they can be applied algorithmically.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class PatternOperator:
    pattern_id: str
    pattern_form: str  # e.g. "فاعِل", "مَفعول", "استَفعَلَ"
    family: str  # mujarrad|mazeed|noun_derivative|masdar|nisba|diminutive|plural
    operator_vector: dict[str, float]
    certainty_policy: str
    examples: list[str]

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "pattern_form": self.pattern_form,
            "family": self.family,
            "operator_vector": self.operator_vector,
            "certainty_policy": self.certainty_policy,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PatternOperator":
        return cls(**d)


# Built-in operator vectors for the most important Arabic patterns.
_BUILTIN_PATTERNS: list[dict] = [
    {
        "pattern_id": "faail",
        "pattern_form": "فاعِل",
        "family": "noun_derivative",
        "operator_vector": {"agency": 1.0, "patienthood": 0.0, "causation": 0.3,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.1, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["كاتِب", "عالِم", "قارِئ", "زارِع", "عامِل"],
    },
    {
        "pattern_id": "mafuul",
        "pattern_form": "مَفعول",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.0, "patienthood": 1.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["مَكتوب", "مَعلوم", "مَزروع", "مَصنوع", "مَفتوح"],
    },
    {
        "pattern_id": "mafal_place",
        "pattern_form": "مَفعَل",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 1.0, "instrument": 0.5, "time": 0.5,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["مَكتَب", "مَدخَل", "مَخرَج"],
    },
    {
        "pattern_id": "mafala_place",
        "pattern_form": "مَفعَلة",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 1.0, "instrument": 0.3, "time": 0.2,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["مَكتَبة", "مَزرَعة", "مَدرَسة"],
    },
    {
        "pattern_id": "faaaal_intense",
        "pattern_form": "فَعَّال",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.7, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 1.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.3, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["كَرَّام", "فَعَّال", "صَنَّاع"],
    },
    {
        "pattern_id": "istafala_verb",
        "pattern_form": "استَفعَلَ",
        "family": "mazeed",
        "operator_vector": {"agency": 0.7, "patienthood": 0.0, "causation": 0.5,
                            "intensification": 0.0, "request": 0.9, "reflexivity": 0.5,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["استَخرَجَ", "استَعلَمَ", "استَفتَحَ", "استَأذَنَ"],
    },
    {
        "pattern_id": "tafaala_reflex",
        "pattern_form": "تَفعَّلَ",
        "family": "mazeed",
        "operator_vector": {"agency": 0.5, "patienthood": 0.3, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.8,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 1.0},
        "certainty_policy": "qiyasi",
        "examples": ["تَعَلَّمَ", "تَكَرَّمَ", "تَفَتَّحَ"],
    },
    {
        "pattern_id": "faiil_attr",
        "pattern_form": "فَعيل",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.2, "patienthood": 0.3, "causation": 0.0,
                            "intensification": 0.2, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.7, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["كَريم", "حَسيب", "عَليم", "قَدير"],
    },
    {
        "pattern_id": "fuayyil_dim",
        "pattern_form": "فُعَيِّل",
        "family": "diminutive",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 1.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["كُتَيِّب", "بُيَيِّت", "رُجَيِّل"],
    },
    {
        "pattern_id": "afaal_plural",
        "pattern_form": "أفعال",
        "family": "plural",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 1.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "samai",
        "examples": ["أفعال", "أقوال", "أعمال", "أجمال"],
    },
    {
        "pattern_id": "fiaal_plural",
        "pattern_form": "فِعَال",
        "family": "plural",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 1.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "samai",
        "examples": ["رِجال", "جِبال", "كِتاب→كِتاب"],
    },
    {
        "pattern_id": "fuuul_plural",
        "pattern_form": "فُعول",
        "family": "plural",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 1.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "samai",
        "examples": ["كُتُب", "بُيوت", "قُلوب", "عُلوم"],
    },
    {
        "pattern_id": "fual_plural",
        "pattern_form": "فُعَل",
        "family": "plural",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 1.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "samai",
        "examples": ["دُوَل", "صُوَر", "حُجَج"],
    },
    {
        "pattern_id": "nisba_yaa",
        "pattern_form": "فَعَليّ",
        "family": "nisba",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 1.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["عَرَبيّ", "زِراعيّ", "عِلميّ", "صِناعيّ"],
    },
    {
        "pattern_id": "mustafl_patient",
        "pattern_form": "مُستَفعَل",
        "family": "noun_derivative",
        "operator_vector": {"agency": 0.0, "patienthood": 1.0, "causation": 0.3,
                            "intensification": 0.0, "request": 0.5, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["مُستَخرَج", "مُستَعمَل", "مُستَفتَح"],
    },
    {
        "pattern_id": "mufaail_agent",
        "pattern_form": "مُفاعِل",
        "family": "noun_derivative",
        "operator_vector": {"agency": 1.0, "patienthood": 0.0, "causation": 0.4,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.3,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0},
        "certainty_policy": "qiyasi",
        "examples": ["مُزارِع", "مُكاتِب", "مُعامِل"],
    },
    {
        "pattern_id": "fiaala_masdar_craft",
        "pattern_form": "فِعالة",
        "family": "masdar",
        "operator_vector": {"agency": 0.0, "patienthood": 0.0, "causation": 0.0,
                            "intensification": 0.0, "request": 0.0, "reflexivity": 0.0,
                            "place": 0.0, "instrument": 0.0, "time": 0.0,
                            "nisba": 0.0, "diminutive": 0.0, "plurality": 0.0,
                            "comparison": 0.0, "mutawaa": 0.0,
                            "event_abstraction": 1.0, "craft_profession": 1.0},
        "certainty_policy": "qiyasi",
        "examples": ["زِراعة", "صِناعة", "تِجارة", "كِتابة"],
    },
]


class PatternOperatorRegistry:
    """Registry of Arabic morphological pattern operators."""

    def __init__(self) -> None:
        self._patterns: dict[str, PatternOperator] = {}
        self._load()

    def _load(self) -> None:
        # Load from built-in list first
        for d in _BUILTIN_PATTERNS:
            op = PatternOperator(**d)
            self._patterns[op.pattern_id] = op
        # Overlay with data file if present
        path = _DATA_DIR / "pattern_operator_registry.json"
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for d in data.get("patterns", []):
                op = PatternOperator(**d)
                self._patterns[op.pattern_id] = op
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            pass

    def get(self, pattern_id: str) -> Optional[PatternOperator]:
        return self._patterns.get(pattern_id)

    def find_by_form(self, form: str) -> Optional[PatternOperator]:
        from mcd.morphosemantics.morphophonological_normalizer import MorphophonologicalNormalizer
        norm = MorphophonologicalNormalizer()
        form_stripped = norm.normalize_str(form)
        for op in self._patterns.values():
            if op.pattern_form == form:
                return op
            if norm.normalize_str(op.pattern_form) == form_stripped:
                return op
        return None

    def all(self) -> list[PatternOperator]:
        return list(self._patterns.values())

    def to_dict(self) -> dict:
        return {"patterns": [p.to_dict() for p in self._patterns.values()]}
