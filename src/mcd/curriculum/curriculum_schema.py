"""Shared constants and schema definitions for the Curriculum package."""
from __future__ import annotations

VALID_LEVELS: list[int] = [1, 2, 3, 4, 5, 6, 7, 8]

VALID_TARGET_LAYERS: list[str] = [
    "thing", "property", "action", "relation",
    "cause", "effect", "instrument", "time", "place",
    "evidence", "certainty", "mixed_reasoning",
]

VALID_CERTAINTY_POLICIES: list[str] = [
    "certain_knowledge",
    "probable_knowledge",
    "possible_knowledge",
    "insufficient_evidence",
    "near_certainty",
    "suspend_judgment",
]

VALID_DIFFICULTIES: list[str] = ["easy", "medium", "hard", "adversarial"]

LEVEL_NAMES: dict[int, str] = {
    1: "things",
    2: "properties",
    3: "actions",
    4: "relations",
    5: "causes_effects",
    6: "instruments_times_places",
    7: "evidence_certainty",
    8: "mixed_reasoning",
}

LEVEL_PRIMARY_LAYERS: dict[int, list[str]] = {
    1: ["thing"],
    2: ["property"],
    3: ["action"],
    4: ["relation"],
    5: ["cause", "effect"],
    6: ["instrument", "time", "place"],
    7: ["evidence", "certainty"],
    8: ["mixed_reasoning"],
}
