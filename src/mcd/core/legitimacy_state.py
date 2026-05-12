"""Transition legitimacy state."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegitimacyState:
    context_valid: bool
    evidence_valid: bool
    rank_valid: bool
    contradiction_free: bool
    governance_passed: bool

    @property
    def legitimate(self) -> bool:
        return (
            self.context_valid
            and self.evidence_valid
            and self.rank_valid
            and self.contradiction_free
            and self.governance_passed
        )
