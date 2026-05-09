"""RealityFrame and RelationTriple dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RelationTriple:
    source: str
    relation: str
    target: str
    qualifier: str | None = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "qualifier": self.qualifier,
        }


@dataclass
class RealityFrame:
    things: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    patients: list[str] = field(default_factory=list)
    instruments: list[str] = field(default_factory=list)
    times: list[str] = field(default_factory=list)
    places: list[str] = field(default_factory=list)
    causes: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    relations: list[RelationTriple] = field(default_factory=list)
    evidence_need: list[str] = field(default_factory=list)
    certainty_policy: str = "probable_knowledge"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "things": self.things,
            "properties": self.properties,
            "actions": self.actions,
            "agents": self.agents,
            "patients": self.patients,
            "instruments": self.instruments,
            "times": self.times,
            "places": self.places,
            "causes": self.causes,
            "effects": self.effects,
            "relations": [r.to_dict() for r in self.relations],
            "evidence_need": self.evidence_need,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }
