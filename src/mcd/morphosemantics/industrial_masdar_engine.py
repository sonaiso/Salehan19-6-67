"""IndustrialMasdarEngine — resolves masdar forms for industrial/professional domains.

Extends the masdar event ontology to handle specialized فِعالة and فَعل masdars
in professional, industrial, and institutional contexts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.masdar_event_ontology import MasdarEvent, load_masdar_events


@dataclass
class IndustrialMasdarResult:
    masdar: str
    root_id: str
    professional_domain: str
    industry_score: float
    social_score: float
    cognitive_score: float
    event_class: str

    def to_dict(self) -> dict:
        return {
            "masdar": self.masdar,
            "root_id": self.root_id,
            "professional_domain": self.professional_domain,
            "industry_score": self.industry_score,
            "social_score": self.social_score,
            "cognitive_score": self.cognitive_score,
            "event_class": self.event_class,
        }


_DOMAIN_MAP: dict[str, str] = {
    "craft": "industrial",
    "profession": "professional",
    "cognitive": "academic",
    "social": "social",
    "motion": "physical",
    "speech": "communicative",
    "impact": "physical",
    "transformation": "industrial",
    "psychological": "psychological",
    "perception": "sensory",
    "color_state": "descriptive",
    "state": "state",
}


class IndustrialMasdarEngine:
    def __init__(self) -> None:
        self._events = {ev.masdar: ev for ev in load_masdar_events()}

    def analyse(self, masdar: str) -> Optional[IndustrialMasdarResult]:
        ev = self._events.get(masdar)
        if ev is None:
            return None
        domain = _DOMAIN_MAP.get(ev.event_class, "general")
        ov = ev.event_vector
        return IndustrialMasdarResult(
            masdar=masdar,
            root_id=ev.root_id,
            professional_domain=domain,
            industry_score=ov.get("craft", 0.0),
            social_score=ov.get("social", 0.0),
            cognitive_score=ov.get("cognitive", 0.0),
            event_class=ev.event_class,
        )
