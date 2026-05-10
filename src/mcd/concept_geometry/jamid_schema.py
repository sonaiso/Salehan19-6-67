"""JamidEssence — Essence Geometry for primitive Arabic nouns.

الجامد = مركز الماهية:
  يثبّت جنس المفهوم، نوعه، فصله، خصائصه الذاتية.
  لا يصدر شهادة. لا ينشئ دليلاً.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EssenceType(str, Enum):
    GENUS = "genus"
    SPECIES = "species"
    DIFFERENTIA = "differentia"
    INDIVIDUAL = "individual"
    MATERIAL = "material"
    LIVING_BEING = "living_being"
    ARTIFACT = "artifact"
    TOOL = "tool"
    PLACE = "place"
    INSTITUTION = "institution"
    ABSTRACT_CONCEPT = "abstract_concept"
    NATURAL_OBJECT = "natural_object"
    UNKNOWN = "unknown"


@dataclass
class JamidEssence:
    """Full Jamid Essence schema with CFK-compatible fields."""
    essence_id: str
    surface: str
    normalized: str
    essence_type: EssenceType
    genus: str
    species: str
    differentia: list[str] = field(default_factory=list)
    intrinsic_properties: list[str] = field(default_factory=list)
    accidental_properties: list[str] = field(default_factory=list)
    part_whole_relations: list[str] = field(default_factory=list)
    ownership_relations: list[str] = field(default_factory=list)
    plural_forms: list[str] = field(default_factory=list)
    diminutive_forms: list[str] = field(default_factory=list)
    nisba_forms: list[str] = field(default_factory=list)
    essence_vector: dict[str, float] = field(default_factory=dict)
    domain_vector: dict[str, float] = field(default_factory=dict)
    trace_refs: list[str] = field(default_factory=list)
    evidence_state: str = "missing"  # always missing — jamid never creates evidence
    certainty_policy: str = "context_required"

    # ── Hard rules ──────────────────────────────────────────────────────────
    can_create_evidence: bool = False      # immutable
    can_issue_certificate: bool = False    # immutable

    def __post_init__(self) -> None:
        # Enforce hard rules — Jamid NEVER creates evidence or issues certificate
        object.__setattr__(self, "can_create_evidence", False)
        object.__setattr__(self, "can_issue_certificate", False)

    def to_dict(self) -> dict:
        return {
            "essence_id": self.essence_id,
            "surface": self.surface,
            "normalized": self.normalized,
            "essence_type": self.essence_type.value if isinstance(self.essence_type, EssenceType) else self.essence_type,
            "genus": self.genus,
            "species": self.species,
            "differentia": self.differentia,
            "intrinsic_properties": self.intrinsic_properties,
            "accidental_properties": self.accidental_properties,
            "part_whole_relations": self.part_whole_relations,
            "ownership_relations": self.ownership_relations,
            "plural_forms": self.plural_forms,
            "diminutive_forms": self.diminutive_forms,
            "nisba_forms": self.nisba_forms,
            "essence_vector": self.essence_vector,
            "domain_vector": self.domain_vector,
            "trace_refs": self.trace_refs,
            "evidence_state": self.evidence_state,
            "certainty_policy": self.certainty_policy,
            "can_create_evidence": False,
            "can_issue_certificate": False,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "JamidEssence":
        d = dict(d)
        d.pop("can_create_evidence", None)
        d.pop("can_issue_certificate", None)
        et = d.get("essence_type", "unknown")
        try:
            d["essence_type"] = EssenceType(et)
        except ValueError:
            d["essence_type"] = EssenceType.UNKNOWN
        return cls(**d)

    @classmethod
    def make(cls, surface: str, essence_type: EssenceType, genus: str, species: str,
             differentia: Optional[list[str]] = None, **kwargs) -> "JamidEssence":
        return cls(
            essence_id=f"JE-{uuid.uuid4().hex[:10]}",
            surface=surface,
            normalized=surface,
            essence_type=essence_type,
            genus=genus,
            species=species,
            differentia=differentia or [],
            **kwargs,
        )
