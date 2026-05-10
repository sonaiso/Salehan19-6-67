"""IrabCase — Arabic I'rab case definitions and registry."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "murab"


@dataclass
class IrabCase:
    case_id: str
    name_ar: str
    name_en: str
    grammatical_function: str
    common_roles: list
    possible_markers: list
    semantic_projection: str
    certainty_effect: float

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "grammatical_function": self.grammatical_function,
            "common_roles": self.common_roles,
            "possible_markers": self.possible_markers,
            "semantic_projection": self.semantic_projection,
            "certainty_effect": self.certainty_effect,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IrabCase":
        return cls(**d)


def load_irab_case_registry() -> dict:
    """Load IrabCase registry from JSON file."""
    path = _DATA_DIR / "irab_case_registry.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {k: IrabCase.from_dict(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return {}
