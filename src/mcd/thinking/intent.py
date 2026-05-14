"""Governed user-intent frame models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

IntentStatus = Literal["explicit", "inferred", "ambiguous", "missing"]


@dataclass
class UserIntentFrame:
    intent_id: str
    raw_request: str
    normalized_request: str = ""
    inferred_intent: str = ""
    intent_status: IntentStatus = "missing"
    uncertainty_preserved: bool = False
    residuals: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)

    def has_intent(self) -> bool:
        return self.intent_status != "missing" and bool((self.inferred_intent or self.normalized_request).strip())
