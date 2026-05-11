"""ConceptCenter — the multi-axis semantic representation of an Arabic word.

The ConceptCenter aggregates all morphosemantic axes into a unified vector
space that represents the word's cognitive centre: essence, event, attribute,
agency, patienthood, causation, instrument, time/place, nisba, comparison,
plurality, context, evidence, and certainty.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConceptCenter:
    concept_id: str
    surface_forms: list[str]
    root_family: str
    essence_axis: dict[str, float]
    event_axis: dict[str, float]
    attribute_axis: dict[str, float]
    agency_axis: dict[str, float]
    patienthood_axis: dict[str, float]
    causation_axis: dict[str, float]
    instrument_axis: dict[str, float]
    time_place_axis: dict[str, float]
    nisba_axis: dict[str, float]
    comparison_axis: dict[str, float]
    plurality_axis: dict[str, float]
    context_axis: dict[str, float]
    evidence_axis: dict[str, float]
    certainty_axis: dict[str, float]
    trace_ids: list[str]

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
            "nisba_axis": self.nisba_axis,
            "comparison_axis": self.comparison_axis,
            "plurality_axis": self.plurality_axis,
            "context_axis": self.context_axis,
            "evidence_axis": self.evidence_axis,
            "certainty_axis": self.certainty_axis,
            "trace_ids": self.trace_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ConceptCenter":
        return cls(**d)


def empty_concept_center(word: str, root_family: str = "") -> ConceptCenter:
    """Create a zeroed ConceptCenter for a given word."""
    return ConceptCenter(
        concept_id=f"CC-{uuid.uuid4().hex[:10]}",
        surface_forms=[word],
        root_family=root_family,
        essence_axis={},
        event_axis={},
        attribute_axis={},
        agency_axis={},
        patienthood_axis={},
        causation_axis={},
        instrument_axis={},
        time_place_axis={},
        nisba_axis={},
        comparison_axis={},
        plurality_axis={},
        context_axis={},
        evidence_axis={},
        certainty_axis={},
        trace_ids=[],
    )
