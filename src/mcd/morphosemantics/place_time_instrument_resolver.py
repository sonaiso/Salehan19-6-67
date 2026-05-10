"""PlaceTimeInstrumentResolver — resolves place/time/instrument semantics from patterns.

Patterns such as مَفعَل, مَفعِل, مَفعَلة encode place/instrument/time of the
action (اسم المكان والزمان والآلة).  This module resolves those roles.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry


@dataclass
class PlaceTimeInstrumentResult:
    word: str
    pattern_id: str
    place_score: float
    time_score: float
    instrument_score: float
    primary_role: str  # place|time|instrument|neutral
    certainty: float

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "pattern_id": self.pattern_id,
            "place_score": self.place_score,
            "time_score": self.time_score,
            "instrument_score": self.instrument_score,
            "primary_role": self.primary_role,
            "certainty": self.certainty,
        }


class PlaceTimeInstrumentResolver:
    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()

    def resolve(self, word: str, pattern_id: str) -> PlaceTimeInstrumentResult:
        op = self._registry.get(pattern_id)
        ov = op.operator_vector if op else {}
        place = ov.get("place", 0.0)
        time = ov.get("time", 0.0)
        instrument = ov.get("instrument", 0.0)

        scores = {"place": place, "time": time, "instrument": instrument}
        primary = max(scores, key=lambda k: scores[k])
        certainty = scores[primary]
        if certainty < 0.3:
            primary = "neutral"

        return PlaceTimeInstrumentResult(
            word=word,
            pattern_id=pattern_id,
            place_score=place,
            time_score=time,
            instrument_score=instrument,
            primary_role=primary,
            certainty=certainty,
        )
