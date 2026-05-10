"""ConceptCenter (Phase 8.3) — CFK-integrated multi-axis concept center.

Collects Jamid and Mushtaq into a unified center. Does NOT certify or create evidence.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from mcd.concept_geometry.jamid_schema import JamidEssence
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit


@dataclass
class ConceptCenter:
    """CFK-integrated concept center. Collects axes, never certifies."""
    concept_id: str
    surface_forms: list[str]
    root_family: str
    jamid_essence_refs: list[str] = field(default_factory=list)
    mushtaq_refs: list[str] = field(default_factory=list)
    essence_axis: dict[str, float] = field(default_factory=dict)
    event_axis: dict[str, float] = field(default_factory=dict)
    attribute_axis: dict[str, float] = field(default_factory=dict)
    agency_axis: list[str] = field(default_factory=list)
    patienthood_axis: list[str] = field(default_factory=list)
    instrument_axis: list[str] = field(default_factory=list)
    time_place_axis: list[str] = field(default_factory=list)
    nisba_axis: list[str] = field(default_factory=list)
    comparison_axis: list[str] = field(default_factory=list)
    plurality_axis: list[str] = field(default_factory=list)
    evidence_axis: dict[str, float] = field(default_factory=dict)
    certainty_axis: str = "context_required"
    trace_refs: list[str] = field(default_factory=list)
    proof_refs: list[str] = field(default_factory=list)

    # Hard rules
    can_create_evidence: bool = False
    can_issue_certificate: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "can_create_evidence", False)
        object.__setattr__(self, "can_issue_certificate", False)

    def to_dict(self) -> dict:
        return {
            "concept_id": self.concept_id,
            "surface_forms": self.surface_forms,
            "root_family": self.root_family,
            "jamid_essence_refs": self.jamid_essence_refs,
            "mushtaq_refs": self.mushtaq_refs,
            "essence_axis": self.essence_axis,
            "event_axis": self.event_axis,
            "attribute_axis": self.attribute_axis,
            "agency_axis": self.agency_axis,
            "patienthood_axis": self.patienthood_axis,
            "instrument_axis": self.instrument_axis,
            "time_place_axis": self.time_place_axis,
            "nisba_axis": self.nisba_axis,
            "comparison_axis": self.comparison_axis,
            "plurality_axis": self.plurality_axis,
            "evidence_axis": self.evidence_axis,
            "certainty_axis": self.certainty_axis,
            "trace_refs": self.trace_refs,
            "proof_refs": self.proof_refs,
            "can_create_evidence": False,
            "can_issue_certificate": False,
        }


def build_concept_center(
    root_family: str,
    surface_forms: list[str],
    jamid_essences: Optional[list[JamidEssence]] = None,
    mushtaq_units: Optional[list[MushtaqUnit]] = None,
) -> ConceptCenter:
    """Build a ConceptCenter from Jamid and Mushtaq inputs."""
    jamid_essences = jamid_essences or []
    mushtaq_units = mushtaq_units or []

    agency: list[str] = []
    patienthood: list[str] = []
    instrument: list[str] = []
    time_place: list[str] = []
    nisba: list[str] = []
    comparison: list[str] = []
    event_axis: dict[str, float] = {}
    essence_axis: dict[str, float] = {}
    attribute_axis: dict[str, float] = {}

    for je in jamid_essences:
        essence_axis.update(je.essence_vector)

    for mu in mushtaq_units:
        from mcd.concept_geometry.mushtaq_schema import ProjectedRelation
        rel = mu.projected_relation
        if rel == ProjectedRelation.AGENT_OF:
            agency.append(mu.surface)
        elif rel == ProjectedRelation.PATIENT_OF:
            patienthood.append(mu.surface)
        elif rel == ProjectedRelation.INSTRUMENT_OF:
            instrument.append(mu.surface)
        elif rel in (ProjectedRelation.PLACE_OF, ProjectedRelation.TIME_OF):
            time_place.append(mu.surface)
        elif rel == ProjectedRelation.ATTRIBUTED_TO:
            nisba.append(mu.surface)
        elif rel == ProjectedRelation.COMPARATIVE_PROPERTY:
            comparison.append(mu.surface)
        elif rel == ProjectedRelation.HAS_PROPERTY:
            attribute_axis[mu.surface] = 1.0
        if mu.folded_event:
            event_axis[mu.folded_event] = event_axis.get(mu.folded_event, 0.0) + 0.5

    return ConceptCenter(
        concept_id=f"CC8-{uuid.uuid4().hex[:10]}",
        surface_forms=surface_forms,
        root_family=root_family,
        jamid_essence_refs=[je.essence_id for je in jamid_essences],
        mushtaq_refs=[mu.mushtaq_id for mu in mushtaq_units],
        essence_axis=essence_axis,
        event_axis=event_axis,
        attribute_axis=attribute_axis,
        agency_axis=agency,
        patienthood_axis=patienthood,
        instrument_axis=instrument,
        time_place_axis=time_place,
        nisba_axis=nisba,
        comparison_axis=comparison,
    )
