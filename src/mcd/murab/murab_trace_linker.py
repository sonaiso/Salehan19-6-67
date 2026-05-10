"""MurabTraceLinker — links I'rab analysis back to source token positions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mcd.murab.murab_schema import MurabUnit


@dataclass
class TraceLink:
    unit_id: str
    token_id: str
    char_start: int
    char_end: int
    estimated: bool
    reason: str
    governing_factor_id: Optional[str]

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "token_id": self.token_id,
            "char_range": [self.char_start, self.char_end],
            "estimated": self.estimated,
            "reason": self.reason,
            "governing_factor_id": self.governing_factor_id,
        }


class MurabTraceLinker:
    """Links a MurabUnit to its original token position in the source text."""

    def link(
        self,
        murab_unit: MurabUnit,
        token_id: str,
        unicode_char_start: int,
        unicode_char_end: int,
    ) -> dict:
        trace = TraceLink(
            unit_id=murab_unit.unit_id,
            token_id=token_id,
            char_start=unicode_char_start,
            char_end=unicode_char_end,
            estimated=murab_unit.marker_visibility in ("estimated", "local"),
            reason="direct_token_alignment",
            governing_factor_id=murab_unit.governing_factor_id,
        )
        return trace.to_dict()

    def link_estimated(
        self,
        murab_unit: MurabUnit,
        reason: str,
    ) -> dict:
        trace = TraceLink(
            unit_id=murab_unit.unit_id,
            token_id=murab_unit.token_id,
            char_start=-1,
            char_end=-1,
            estimated=True,
            reason=reason,
            governing_factor_id=murab_unit.governing_factor_id,
        )
        return trace.to_dict()
