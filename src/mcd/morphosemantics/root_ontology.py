"""RootNode — the semantic nucleus of Arabic morphology.

A root is not merely a set of consonants: it is a centre of meaning potential
that can be activated through patterns to produce an open-ended family of
derived words.  The RootNode dataclass encodes that potential explicitly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class RootNode:
    root_id: str
    radicals: list[str]
    root_type: str  # triliteral|quadriliteral|weak|doubled|hamzated|hollow|defective|assimilated
    semantic_core: str
    sensory_domains: list[str]
    event_potential: list[str]
    transitivity_potential: str  # transitive|intransitive|both
    causation_potential: float  # 0.0-1.0
    metaphor_potential: float  # 0.0-1.0
    examples: list[str]
    certainty: float  # 0.0-1.0

    def to_dict(self) -> dict:
        return {
            "root_id": self.root_id,
            "radicals": self.radicals,
            "root_type": self.root_type,
            "semantic_core": self.semantic_core,
            "sensory_domains": self.sensory_domains,
            "event_potential": self.event_potential,
            "transitivity_potential": self.transitivity_potential,
            "causation_potential": self.causation_potential,
            "metaphor_potential": self.metaphor_potential,
            "examples": self.examples,
            "certainty": self.certainty,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RootNode":
        return cls(**d)


def load_root_ontology() -> list[RootNode]:
    """Load all root nodes from the seed data file. Returns [] on any error."""
    path = _DATA_DIR / "root_ontology_seed_ar.jsonl"
    nodes: list[RootNode] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    nodes.append(RootNode(**json.loads(line)))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return nodes


def get_root_by_id(root_id: str) -> Optional[RootNode]:
    """Return the first RootNode whose root_id matches, or None."""
    for node in load_root_ontology():
        if node.root_id == root_id:
            return node
    return None


def get_root_by_radicals(radicals: list[str]) -> Optional[RootNode]:
    """Return the first RootNode whose radicals match (order-sensitive), or None."""
    for node in load_root_ontology():
        if node.radicals == radicals:
            return node
    return None
