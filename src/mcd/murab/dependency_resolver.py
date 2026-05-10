"""DependencyResolver — resolves head-dependent relations in Arabic."""
from __future__ import annotations
from mcd.murab.murab_schema import MurabUnit
from dataclasses import dataclass


@dataclass
class DependencyRelation:
    head_id: str
    dependent_id: str
    relation_type: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "head_id": self.head_id,
            "dependent_id": self.dependent_id,
            "relation_type": self.relation_type,
            "certainty": self.certainty,
        }


class DependencyResolver:
    """Resolves head-dependent syntactic relations."""

    def resolve(self, units: list) -> list:
        """Resolve dependency relations for a list of MurabUnit objects."""
        relations = []

        for i, unit in enumerate(units):
            if unit.syntactic_role == "agent" and i > 0:
                head = units[i - 1]
                relations.append(DependencyRelation(
                    head_id=head.unit_id,
                    dependent_id=unit.unit_id,
                    relation_type="nsubj",
                    certainty=0.8,
                ))
            elif unit.syntactic_role == "object" and i > 0:
                head = units[i - 1]
                relations.append(DependencyRelation(
                    head_id=head.unit_id,
                    dependent_id=unit.unit_id,
                    relation_type="obj",
                    certainty=0.8,
                ))
            elif unit.syntactic_role == "object_of_preposition" and i > 1:
                head = units[i - 2]
                relations.append(DependencyRelation(
                    head_id=head.unit_id,
                    dependent_id=unit.unit_id,
                    relation_type="obl",
                    certainty=0.75,
                ))

        return relations
