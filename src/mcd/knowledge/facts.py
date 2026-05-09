"""Fact dataclass and FactStore."""
from __future__ import annotations

from dataclasses import dataclass, field
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty


@dataclass
class Fact:
    fact_id: str
    claim: str
    source_ids: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    certainty: Certainty = field(default_factory=lambda: Certainty.from_score(0.5))


class FactStore:
    def __init__(self) -> None:
        self._store: dict[str, Fact] = {}

    def add(self, fact: Fact) -> None:
        self._store[fact.fact_id] = fact

    def get(self, fact_id: str) -> Fact | None:
        return self._store.get(fact_id)

    def find_by_claim(self, claim: str) -> list[Fact]:
        return [f for f in self._store.values() if claim.lower() in f.claim.lower()]

    def all(self) -> list[Fact]:
        return list(self._store.values())
