"""QiyasiSamaiShadhRegistry — classifies Arabic words as regular (قياسي),
heard (سماعي), or anomalous (شاذ).

In Arabic morphological tradition:
- قياسي (qiyasi): follows a productive, rule-based pattern
- سماعي (samai): attested by usage but not fully predictable
- شاذ (shadh): irregular, anomalous, does not follow the standard pattern
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class QSSEntry:
    word: str
    classification: str  # qiyasi|samai|shadh
    pattern_id: str
    notes: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "classification": self.classification,
            "pattern_id": self.pattern_id,
            "notes": self.notes,
            "certainty": self.certainty,
        }


_BUILTIN: list[dict] = [
    {"word": "كاتِب", "classification": "qiyasi", "pattern_id": "faail",
     "notes": "Standard فاعِل agent noun from ك-ت-ب", "certainty": 1.0},
    {"word": "مَكتوب", "classification": "qiyasi", "pattern_id": "mafuul",
     "notes": "Standard مَفعول passive participle", "certainty": 1.0},
    {"word": "كُتُب", "classification": "samai", "pattern_id": "fuuul_plural",
     "notes": "Heard broken plural of كِتاب", "certainty": 0.95},
    {"word": "رِجال", "classification": "samai", "pattern_id": "fiaal_plural",
     "notes": "Heard broken plural of رَجُل", "certainty": 1.0},
    {"word": "عالِم", "classification": "qiyasi", "pattern_id": "faail",
     "notes": "Standard فاعِل from ع-ل-م", "certainty": 1.0},
    {"word": "مَعلوم", "classification": "qiyasi", "pattern_id": "mafuul",
     "notes": "Standard مَفعول from ع-ل-م", "certainty": 1.0},
    {"word": "زِراعة", "classification": "qiyasi", "pattern_id": "fiaala_masdar_craft",
     "notes": "Masdar craft pattern", "certainty": 0.95},
    {"word": "مُزارِع", "classification": "qiyasi", "pattern_id": "mufaail_agent",
     "notes": "Form-III agent noun", "certainty": 1.0},
    {"word": "استَخرَجَ", "classification": "qiyasi", "pattern_id": "istafala_verb",
     "notes": "Form-X verb from خ-ر-ج", "certainty": 1.0},
    {"word": "عَرَبيّ", "classification": "qiyasi", "pattern_id": "nisba_yaa",
     "notes": "Nisba adjective from عَرَب", "certainty": 1.0},
    {"word": "كُتَيِّب", "classification": "qiyasi", "pattern_id": "fuayyil_dim",
     "notes": "Diminutive of كِتاب", "certainty": 0.9},
    {"word": "أفعال", "classification": "qiyasi", "pattern_id": "afaal_plural",
     "notes": "Qiyasi broken plural pattern", "certainty": 0.85},
    {"word": "جاء", "classification": "shadh", "pattern_id": "hollow",
     "notes": "Hollow verb with irregular conjugation", "certainty": 0.9},
    {"word": "قال", "classification": "shadh", "pattern_id": "hollow",
     "notes": "Hollow verb from ق-و-ل", "certainty": 0.9},
]


class QiyasiSamaiShadhRegistry:
    """Registry mapping words to their qiyasi/samai/shadh status."""

    def __init__(self) -> None:
        self._data: dict[str, QSSEntry] = {}
        for d in _BUILTIN:
            e = QSSEntry(**d)
            self._data[e.word] = e
        self._load()

    def _load(self) -> None:
        path = _DATA_DIR / "qiyasi_samai_shadh_seed.jsonl"
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        d = json.loads(line)
                        e = QSSEntry(**d)
                        self._data[e.word] = e
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            pass

    def classify(self, word: str) -> Optional[QSSEntry]:
        return self._data.get(word)

    def all_entries(self) -> list[QSSEntry]:
        return list(self._data.values())
