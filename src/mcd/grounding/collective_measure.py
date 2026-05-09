"""CollectiveMeasure — models collective measures and their basis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


_FREEDOM_KEYWORDS = {"الحرية", "حرية", "الحريات"}
_CIVILIZATIONAL_KEYWORDS = {"الحرية", "العدالة", "الديمقراطية", "الإسلام", "المساواة"}
_SYSTEMIC_KEYWORDS = {"قانون", "نظام", "دستور", "مؤسسة"}


@dataclass
class CollectiveMeasureFrame:
    measure: str
    source_concept: str
    public_acceptance: float = 0.0
    institutional_support: float = 0.0
    behavioral_effects: list[str] = field(default_factory=list)
    civilizational_basis: str = ""
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.3
    warnings: list[str] = field(default_factory=list)


class CollectiveMeasureModel:
    """Analyzes collective measure texts."""

    def analyze(self, measure_text: str) -> CollectiveMeasureFrame:
        words = measure_text.strip().split()
        frame = CollectiveMeasureFrame(
            measure=measure_text,
            source_concept="",
        )

        for word in words:
            # Check if it's a freedom concept (ask: which freedom?)
            if any(kw in word for kw in _FREEDOM_KEYWORDS):
                frame.source_concept = word
                frame.warnings.append("which_freedom_not_specified")
                frame.warnings.append("freedom_is_civilizational_concept")

            # Check civilizational basis
            if any(kw in word for kw in _CIVILIZATIONAL_KEYWORDS):
                frame.civilizational_basis = word

            # Systemic support detection
            if any(kw in word for kw in _SYSTEMIC_KEYWORDS):
                frame.institutional_support = min(1.0, frame.institutional_support + 0.3)

        # If no evidence → certainty stays low and warn
        if not frame.evidence:
            frame.warnings.append("no_evidence_for_collective_measure")
            # certainty stays at 0.3

        # Ask: is this a real measure or just a slogan?
        if not frame.institutional_support:
            frame.warnings.append("may_be_slogan_not_real_measure")

        frame.certainty = max(0.0, min(1.0, frame.certainty))
        return frame
