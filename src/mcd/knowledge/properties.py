"""Property dataclass and PropertyRegistry."""
from __future__ import annotations

from dataclasses import dataclass, field
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty


@dataclass
class Property:
    property_id: str
    names: dict[str, str]
    category: str
    value_type: str
    evidence: list[Evidence] = field(default_factory=list)
    certainty: Certainty = field(default_factory=lambda: Certainty.from_score(0.5))


class PropertyRegistry:
    def __init__(self) -> None:
        self._store: dict[str, Property] = {}

    def add(self, prop: Property) -> None:
        self._store[prop.property_id] = prop

    def get(self, property_id: str) -> Property | None:
        return self._store.get(property_id)

    def all(self) -> list[Property]:
        return list(self._store.values())
