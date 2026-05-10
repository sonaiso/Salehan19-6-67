"""MasdarEvent — the masdar (verbal noun) as an abstract event ontology node.

The masdar in Arabic grammar is the purest abstraction of the verbal event:
it names the event without anchoring it in time, person, or number.  This
module models the masdar as an event node with a class, a vector, and typical
participants.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class MasdarEvent:
    masdar: str
    root_id: str
    pattern: str
    event_class: str  # motion|state|craft|profession|impact|perception|speech|transformation|color_state|psychological|social|cognitive
    event_vector: dict[str, float]
    typical_agent: list[str]
    typical_patient: list[str]
    typical_instrument: list[str]
    typical_domain: list[str]

    def to_dict(self) -> dict:
        return {
            "masdar": self.masdar,
            "root_id": self.root_id,
            "pattern": self.pattern,
            "event_class": self.event_class,
            "event_vector": self.event_vector,
            "typical_agent": self.typical_agent,
            "typical_patient": self.typical_patient,
            "typical_instrument": self.typical_instrument,
            "typical_domain": self.typical_domain,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MasdarEvent":
        return cls(**d)


# Built-in seed events for the most important masdars
_BUILTIN_MASDARS: list[dict] = [
    {
        "masdar": "كِتابة",
        "root_id": "ktb",
        "pattern": "فِعالة",
        "event_class": "craft",
        "event_vector": {"volition": 1.0, "creativity": 0.8, "craft": 1.0,
                         "communication": 0.9, "physical": 0.3},
        "typical_agent": ["كاتِب", "مُؤلِّف"],
        "typical_patient": ["كِتاب", "مَقال", "رِسالة"],
        "typical_instrument": ["قَلَم", "حاسوب"],
        "typical_domain": ["أدب", "عِلم", "صِحافة"],
    },
    {
        "masdar": "زِراعة",
        "root_id": "zraa",
        "pattern": "فِعالة",
        "event_class": "craft",
        "event_vector": {"volition": 1.0, "creativity": 0.5, "craft": 1.0,
                         "physical": 0.9, "natural": 1.0},
        "typical_agent": ["مُزارِع", "فَلَّاح"],
        "typical_patient": ["أرض", "مَحصول", "بَذرة"],
        "typical_instrument": ["مِحراث", "جَرَّار"],
        "typical_domain": ["فِلاحة", "بيئة", "اقتِصاد"],
    },
    {
        "masdar": "عِلم",
        "root_id": "alm",
        "pattern": "فِعل",
        "event_class": "cognitive",
        "event_vector": {"volition": 0.7, "cognitive": 1.0, "social": 0.5,
                         "physical": 0.0, "certainty": 0.9},
        "typical_agent": ["عالِم", "طالِب"],
        "typical_patient": ["مَعلومة", "حَقيقة", "مَسألة"],
        "typical_instrument": ["كِتاب", "تَجرِبة"],
        "typical_domain": ["عُلوم", "تَعليم", "بَحث"],
    },
    {
        "masdar": "خُروج",
        "root_id": "xrj",
        "pattern": "فُعول",
        "event_class": "motion",
        "event_vector": {"volition": 0.8, "motion": 1.0, "direction": 1.0,
                         "physical": 0.9, "social": 0.3},
        "typical_agent": ["شَخص", "حَيوان", "شَيء"],
        "typical_patient": [],
        "typical_instrument": [],
        "typical_domain": ["مَكان", "سَفَر", "حَرَكة"],
    },
    {
        "masdar": "دُخول",
        "root_id": "dxl",
        "pattern": "فُعول",
        "event_class": "motion",
        "event_vector": {"volition": 0.8, "motion": 1.0, "direction": 1.0,
                         "physical": 0.9, "social": 0.3},
        "typical_agent": ["شَخص", "حَيوان"],
        "typical_patient": [],
        "typical_instrument": [],
        "typical_domain": ["مَكان", "سَفَر", "حَرَكة"],
    },
    {
        "masdar": "صُنع",
        "root_id": "snaa",
        "pattern": "فُعل",
        "event_class": "craft",
        "event_vector": {"volition": 1.0, "creativity": 0.9, "craft": 1.0,
                         "physical": 0.8, "transformation": 0.7},
        "typical_agent": ["صانِع", "حِرَفي"],
        "typical_patient": ["مُنتَج", "سِلعة"],
        "typical_instrument": ["آلة", "أداة"],
        "typical_domain": ["صِناعة", "اقتِصاد"],
    },
    {
        "masdar": "قَول",
        "root_id": "qwl",
        "pattern": "فَعل",
        "event_class": "speech",
        "event_vector": {"volition": 1.0, "cognitive": 0.8, "social": 1.0,
                         "communication": 1.0, "physical": 0.1},
        "typical_agent": ["إنسان"],
        "typical_patient": ["كَلام", "رَأي"],
        "typical_instrument": ["لِسان", "قَلَم"],
        "typical_domain": ["لُغة", "خِطاب", "حِوار"],
    },
    {
        "masdar": "فَتح",
        "root_id": "fth",
        "pattern": "فَعل",
        "event_class": "impact",
        "event_vector": {"volition": 1.0, "impact": 1.0, "transformation": 0.7,
                         "physical": 0.8, "social": 0.5},
        "typical_agent": ["قائِد", "شَخص"],
        "typical_patient": ["باب", "مَدينة", "بِلاد"],
        "typical_instrument": ["مِفتاح", "جَيش"],
        "typical_domain": ["حَرب", "تَاريخ", "مَكان"],
    },
]


def load_masdar_events() -> list[MasdarEvent]:
    """Load masdar events, merging built-in and file data."""
    events = [MasdarEvent(**d) for d in _BUILTIN_MASDARS]
    path = _DATA_DIR / "masdar_event_classes.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("events", []):
            events.append(MasdarEvent(**d))
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return events


def get_masdar_by_form(masdar: str) -> Optional[MasdarEvent]:
    for ev in load_masdar_events():
        if ev.masdar == masdar:
            return ev
    return None


def get_masdars_by_root(root_id: str) -> list[MasdarEvent]:
    return [ev for ev in load_masdar_events() if ev.root_id == root_id]
