"""Thing dataclass and ThingRegistry."""
from __future__ import annotations

from dataclasses import dataclass, field
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty


@dataclass
class Thing:
    thing_id: str
    names: dict[str, str]
    haqiqa: str
    properties: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    affordances: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    certainty: Certainty = field(default_factory=lambda: Certainty.from_score(0.5))


class ThingRegistry:
    def __init__(self) -> None:
        self._store: dict[str, Thing] = {}

    def add(self, thing: Thing) -> None:
        self._store[thing.thing_id] = thing

    def get(self, thing_id: str) -> Thing | None:
        return self._store.get(thing_id)

    def find_by_name(self, name: str) -> list[Thing]:
        results = []
        for thing in self._store.values():
            if name in thing.names.values():
                results.append(thing)
            elif any(name in n for n in thing.names.values()):
                results.append(thing)
        return results

    def all(self) -> list[Thing]:
        return list(self._store.values())
