"""IrabMarker — Arabic I'rab marker definitions and registry."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "murab"


@dataclass
class IrabMarker:
    marker_id: str
    unicode_char: str
    name_ar: str
    type: str  # original|substitute|estimated|local
    associated_cases: list

    def to_dict(self) -> dict:
        return {
            "marker_id": self.marker_id,
            "unicode_char": self.unicode_char,
            "name_ar": self.name_ar,
            "type": self.type,
            "associated_cases": self.associated_cases,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IrabMarker":
        return cls(**d)


def load_irab_marker_registry() -> dict:
    """Load IrabMarker registry from JSON file."""
    path = _DATA_DIR / "irab_marker_registry.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {k: IrabMarker.from_dict(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return {}
