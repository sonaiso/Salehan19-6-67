"""ConceptPropagation — models how concepts spread through society."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PropagationChannel(str, Enum):
    LANGUAGE = "language"
    EDUCATION = "education"
    REPETITION = "repetition"
    MEDIA = "media"
    SYSTEM = "system"
    PUBLIC_OPINION = "public_opinion"
    INSTITUTIONAL_ENFORCEMENT = "institutional_enforcement"


@dataclass
class ConceptPropagationFrame:
    concept: str
    carriers: list[str] = field(default_factory=list)
    channels: list[PropagationChannel] = field(default_factory=list)
    adoption_level: float = 0.0
    resistance: float = 0.0
    public_atmosphere_effect: float = 0.0
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.3


class ConceptPropagationModel:
    """Models concept propagation through societal channels."""

    def analyze(
        self,
        concept: str,
        carriers: Optional[list[str]] = None,
        channels: Optional[list[PropagationChannel]] = None,
        evidence: Optional[list[str]] = None,
    ) -> ConceptPropagationFrame:
        frame = ConceptPropagationFrame(
            concept=concept,
            carriers=carriers or [],
            channels=channels or [],
            evidence=evidence or [],
        )

        # Certainty increases with evidence
        if frame.evidence:
            frame.certainty = min(0.7, 0.3 + 0.1 * len(frame.evidence))

        # Adoption level estimate based on channels
        if PropagationChannel.INSTITUTIONAL_ENFORCEMENT in frame.channels:
            frame.adoption_level = min(1.0, frame.adoption_level + 0.4)
        if PropagationChannel.MEDIA in frame.channels:
            frame.adoption_level = min(1.0, frame.adoption_level + 0.2)
        if PropagationChannel.EDUCATION in frame.channels:
            frame.adoption_level = min(1.0, frame.adoption_level + 0.2)

        # Public atmosphere effect
        if PropagationChannel.PUBLIC_OPINION in frame.channels:
            frame.public_atmosphere_effect = 0.5

        return frame
