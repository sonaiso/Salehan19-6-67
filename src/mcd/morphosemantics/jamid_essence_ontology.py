"""JamidEssence — جامد (frozen/primitive) nouns as ontological essences.

Unlike derived (مشتق) words that carry morphological history, jamid nouns
stand on their own as primitive ontological units: the genus (جنس), the
species (نوع), the differentia (فصل), individual, material, artifact, place,
living being, or abstract entity.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class JamidEssence:
    term: str
    essence_type: str  # genus|species|differentia|individual|material|artifact|place|living|abstract
    genus: str
    species: str
    differentia: str
    properties: list[str]
    part_whole_relations: list[str]
    nisba_forms: list[str]
    plural_forms: list[str]
    diminutive_forms: list[str]

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "essence_type": self.essence_type,
            "genus": self.genus,
            "species": self.species,
            "differentia": self.differentia,
            "properties": self.properties,
            "part_whole_relations": self.part_whole_relations,
            "nisba_forms": self.nisba_forms,
            "plural_forms": self.plural_forms,
            "diminutive_forms": self.diminutive_forms,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "JamidEssence":
        return cls(**d)


# A minimal built-in set so tests work without data files
_BUILTIN_ESSENCES: list[dict] = [
    {
        "term": "إنسان",
        "essence_type": "species",
        "genus": "حَيوان",
        "species": "إنسان",
        "differentia": "ناطِق",
        "properties": ["عاقِل", "اجتِماعي", "مُريد"],
        "part_whole_relations": ["جِسم", "عَقل", "رُوح"],
        "nisba_forms": ["إنساني"],
        "plural_forms": ["بَشَر", "أناس", "ناس"],
        "diminutive_forms": ["أُنَيسان"],
    },
    {
        "term": "شَجَرة",
        "essence_type": "living",
        "genus": "نَبات",
        "species": "شَجَرة",
        "differentia": "ذاتُ جِذع",
        "properties": ["يَنمو", "مُثمِر", "مُعمِّر"],
        "part_whole_relations": ["جِذر", "جَذع", "غُصن", "وَرَقة", "ثَمَرة"],
        "nisba_forms": ["شَجَري"],
        "plural_forms": ["أشجار", "شَجَر"],
        "diminutive_forms": ["شُجَيرة"],
    },
    {
        "term": "ماء",
        "essence_type": "material",
        "genus": "مادَّة",
        "species": "سائِل",
        "differentia": "H₂O",
        "properties": ["سائِل", "شَفَّاف", "حَيوي"],
        "part_whole_relations": ["بَحر", "نَهر", "بِئر"],
        "nisba_forms": ["مائي"],
        "plural_forms": ["مِياه"],
        "diminutive_forms": [],
    },
    {
        "term": "كِتاب",
        "essence_type": "artifact",
        "genus": "وِعاء",
        "species": "وِعاء مَعرِفي",
        "differentia": "مَكتوب مُجلَّد",
        "properties": ["يَحمِل مَعرِفة", "مُنظَّم", "قابِل للقِراءة"],
        "part_whole_relations": ["صَفحة", "غِلاف", "فَصل"],
        "nisba_forms": ["كِتابي"],
        "plural_forms": ["كُتُب", "أكتاب"],
        "diminutive_forms": ["كُتَيِّب"],
    },
    {
        "term": "بَيت",
        "essence_type": "artifact",
        "genus": "مَكان",
        "species": "مَسكَن",
        "differentia": "لِلإنسان",
        "properties": ["يُؤوي", "مَبني", "خاص"],
        "part_whole_relations": ["غُرفة", "باب", "نافِذة", "سَقف"],
        "nisba_forms": ["بَيتي"],
        "plural_forms": ["بُيوت", "أبيات"],
        "diminutive_forms": ["بُيَيِّت"],
    },
    {
        "term": "سَماء",
        "essence_type": "place",
        "genus": "فَضاء",
        "species": "غِلاف جَوِّي",
        "differentia": "فوق الأرض",
        "properties": ["واسِع", "أزرَق", "مُضيء"],
        "part_whole_relations": ["غَيم", "شَمس", "نَجم"],
        "nisba_forms": ["سَماوي"],
        "plural_forms": ["سَماوات"],
        "diminutive_forms": [],
    },
]


def load_jamid_essences() -> list[JamidEssence]:
    """Load jamid essences from built-in and data file."""
    essences = [JamidEssence(**d) for d in _BUILTIN_ESSENCES]
    path = _DATA_DIR / "jamid_essence_seed_ar.jsonl"
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    essences.append(JamidEssence(**json.loads(line)))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return essences


def get_jamid_by_term(term: str) -> Optional[JamidEssence]:
    for e in load_jamid_essences():
        if e.term == term:
            return e
    return None
