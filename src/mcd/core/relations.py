"""Relation dataclass and relation type enum."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RelationType(str, Enum):
    IS_PART_OF = "is_part_of"
    HAS_ROOT = "has_root"
    HAS_PATTERN = "has_pattern"
    DENOTES = "denotes"
    ENTAILS = "entails"
    INCLUDES = "includes"
    RESTRICTS = "restricts"
    PREDICATES = "predicates"
    AGENT_OF = "agent_of"
    PATIENT_OF = "patient_of"
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    REQUIRES = "requires"
    PREVENTS = "prevents"
    GENERALIZES = "generalizes"
    SPECIALIZES = "specializes"
    ANALOGIZES = "analogizes"
    EVIDENCES = "evidences"
    CONTRADICTS = "contradicts"


@dataclass
class Relation:
    relation_id: str
    relation_type: str
    source: str
    target: str
    conditions: list[str] = field(default_factory=list)
    evidence: list = field(default_factory=list)
    certainty: float = 0.0

    def to_dict(self) -> dict:
        return {
            "relation_id": self.relation_id,
            "relation_type": self.relation_type,
            "source": self.source,
            "target": self.target,
            "conditions": self.conditions,
            "certainty": self.certainty,
        }
