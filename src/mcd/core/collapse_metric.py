"""Collapse metric for illicit epistemic degradation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CollapseEvent:
    illicit_jump: float
    context_loss: float
    semantic_drift: float
    rank_violation: float


def collapse_score(event: CollapseEvent) -> float:
    return (
        event.illicit_jump
        + event.context_loss
        + event.semantic_drift
        + event.rank_violation
    )
