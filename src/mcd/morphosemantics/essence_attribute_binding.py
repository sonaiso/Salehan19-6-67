"""EssenceAttributeBinding — binding jamid essences to attribute vectors.

Maps a JamidEssence to a structured attribute vector for use in ConceptCenter.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.jamid_essence_ontology import JamidEssence, load_jamid_essences


@dataclass
class EssenceAttributeBinding:
    term: str
    attribute_vector: dict[str, float]
    genus_score: float
    species_score: float
    differentia_score: float
    property_count: int
    part_whole_depth: int

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "attribute_vector": self.attribute_vector,
            "genus_score": self.genus_score,
            "species_score": self.species_score,
            "differentia_score": self.differentia_score,
            "property_count": self.property_count,
            "part_whole_depth": self.part_whole_depth,
        }


def _essence_type_to_vector(essence_type: str) -> dict[str, float]:
    mapping: dict[str, dict[str, float]] = {
        "genus":       {"abstract": 0.8, "natural": 0.5, "artifact": 0.0, "living": 0.0},
        "species":     {"abstract": 0.5, "natural": 0.6, "artifact": 0.0, "living": 0.7},
        "differentia": {"abstract": 0.9, "natural": 0.3, "artifact": 0.0, "living": 0.0},
        "individual":  {"abstract": 0.0, "natural": 0.5, "artifact": 0.4, "living": 0.5},
        "material":    {"abstract": 0.0, "natural": 1.0, "artifact": 0.3, "living": 0.0},
        "artifact":    {"abstract": 0.2, "natural": 0.0, "artifact": 1.0, "living": 0.0},
        "place":       {"abstract": 0.2, "natural": 0.7, "artifact": 0.5, "living": 0.0},
        "living":      {"abstract": 0.0, "natural": 0.8, "artifact": 0.0, "living": 1.0},
        "abstract":    {"abstract": 1.0, "natural": 0.0, "artifact": 0.0, "living": 0.0},
    }
    return mapping.get(essence_type, {"abstract": 0.5, "natural": 0.5, "artifact": 0.0, "living": 0.0})


def bind_essence(essence: JamidEssence) -> EssenceAttributeBinding:
    av = _essence_type_to_vector(essence.essence_type)
    av["property_richness"] = min(1.0, len(essence.properties) / 5.0)
    av["part_whole_richness"] = min(1.0, len(essence.part_whole_relations) / 5.0)
    return EssenceAttributeBinding(
        term=essence.term,
        attribute_vector=av,
        genus_score=0.9 if essence.genus else 0.0,
        species_score=0.9 if essence.species else 0.0,
        differentia_score=0.8 if essence.differentia else 0.0,
        property_count=len(essence.properties),
        part_whole_depth=len(essence.part_whole_relations),
    )


def bind_by_term(term: str) -> Optional[EssenceAttributeBinding]:
    for e in load_jamid_essences():
        if e.term == term:
            return bind_essence(e)
    return None
