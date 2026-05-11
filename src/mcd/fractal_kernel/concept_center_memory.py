from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class ConceptCenterRecord:
    concept_id: str
    surface_forms: list[str] = field(default_factory=list)
    root_family: list[str] = field(default_factory=list)
    essence_axis: str = ""
    event_axis: str = ""
    attribute_axis: str = ""
    agency_axis: str = ""
    patienthood_axis: str = ""
    causation_axis: str = ""
    instrument_axis: str = ""
    time_place_axis: str = ""
    mabni_axis: list[str] = field(default_factory=list)
    murab_axis: list[str] = field(default_factory=list)
    evidence_axis: list[str] = field(default_factory=list)
    certainty_axis: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    proof_refs: list[str] = field(default_factory=list)
    linked_unit_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "concept_id": self.concept_id,
            "surface_forms": self.surface_forms,
            "root_family": self.root_family,
            "essence_axis": self.essence_axis,
            "event_axis": self.event_axis,
            "attribute_axis": self.attribute_axis,
            "agency_axis": self.agency_axis,
            "patienthood_axis": self.patienthood_axis,
            "causation_axis": self.causation_axis,
            "instrument_axis": self.instrument_axis,
            "time_place_axis": self.time_place_axis,
            "mabni_axis": self.mabni_axis,
            "murab_axis": self.murab_axis,
            "evidence_axis": self.evidence_axis,
            "certainty_axis": self.certainty_axis,
            "trace_refs": self.trace_refs,
            "proof_refs": self.proof_refs,
            "linked_unit_ids": self.linked_unit_ids,
        }


class ConceptCenterMemory:
    def __init__(self) -> None:
        self._concepts: dict[str, ConceptCenterRecord] = {}
        self._surface_index: dict[str, list[str]] = {}
        self._root_index: dict[str, list[str]] = {}
        self._domain_index: dict[str, list[str]] = {}

    def add_concept_center(self, record: ConceptCenterRecord) -> None:
        self._concepts[record.concept_id] = record
        for sf in record.surface_forms:
            self._surface_index.setdefault(sf, []).append(record.concept_id)
        for root in record.root_family:
            self._root_index.setdefault(root, []).append(record.concept_id)

    def get_by_concept_id(self, concept_id: str) -> Optional[ConceptCenterRecord]:
        return self._concepts.get(concept_id)

    def search_by_surface(self, surface: str) -> list[ConceptCenterRecord]:
        ids = self._surface_index.get(surface, [])
        return [self._concepts[i] for i in ids if i in self._concepts]

    def search_by_root(self, root: str) -> list[ConceptCenterRecord]:
        ids = self._root_index.get(root, [])
        return [self._concepts[i] for i in ids if i in self._concepts]

    def search_by_domain(self, domain: str) -> list[ConceptCenterRecord]:
        ids = self._domain_index.get(domain, [])
        return [self._concepts[i] for i in ids if i in self._concepts]

    def link_unit_to_concept(self, concept_id: str, unit_id: str) -> bool:
        record = self._concepts.get(concept_id)
        if record is None:
            return False
        if unit_id not in record.linked_unit_ids:
            record.linked_unit_ids.append(unit_id)
        return True

    def export_memory(self) -> list[dict]:
        return [r.to_dict() for r in self._concepts.values()]

    def __len__(self) -> int:
        return len(self._concepts)
