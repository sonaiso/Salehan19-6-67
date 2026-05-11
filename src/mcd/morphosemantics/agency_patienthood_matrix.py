"""AgencyPatienthoodMatrix — maps words to their agency/patienthood roles.

Arabic morphology encodes the agent/patient distinction in the pattern itself.
This module builds a matrix of role vectors from pattern operators applied to
a root family.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.pattern_operator_registry import PatternOperator, PatternOperatorRegistry


@dataclass
class AgencyPatienthoodEntry:
    word: str
    root_id: str
    pattern_id: str
    agency_score: float
    patienthood_score: float
    causation_score: float
    role_label: str  # agent|patient|both|neutral

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "root_id": self.root_id,
            "pattern_id": self.pattern_id,
            "agency_score": self.agency_score,
            "patienthood_score": self.patienthood_score,
            "causation_score": self.causation_score,
            "role_label": self.role_label,
        }


def _role_label(agency: float, patienthood: float) -> str:
    if agency >= 0.7 and patienthood < 0.3:
        return "agent"
    if patienthood >= 0.7 and agency < 0.3:
        return "patient"
    if agency >= 0.4 and patienthood >= 0.4:
        return "both"
    return "neutral"


class AgencyPatienthoodMatrix:
    """Build and query agency/patienthood entries for a set of (word, root, pattern) triples."""

    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()
        self._entries: list[AgencyPatienthoodEntry] = []

    def add(self, word: str, root_id: str, pattern_id: str) -> Optional[AgencyPatienthoodEntry]:
        op = self._registry.get(pattern_id)
        if op is None:
            return None
        ov = op.operator_vector
        entry = AgencyPatienthoodEntry(
            word=word,
            root_id=root_id,
            pattern_id=pattern_id,
            agency_score=ov.get("agency", 0.0),
            patienthood_score=ov.get("patienthood", 0.0),
            causation_score=ov.get("causation", 0.0),
            role_label=_role_label(ov.get("agency", 0.0), ov.get("patienthood", 0.0)),
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> list[AgencyPatienthoodEntry]:
        return list(self._entries)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self._entries]}
