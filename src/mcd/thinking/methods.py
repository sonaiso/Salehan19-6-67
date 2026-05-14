"""Thinking method models and evidence-rank helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MethodType = Literal["rational", "scientific", "formal", "linguistic", "normative", "systemic"]

_EVIDENCE_RANK_ORDER = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "governed": 4,
}


@dataclass
class ThinkingMethod:
    method_id: str
    method_type: MethodType
    required_inputs: list[str]
    allowed_outputs: list[str]
    forbidden_outputs: list[str]
    required_evidence_rank: str = "medium"
    residual_policy: str = "preserve"


def evidence_rank_sufficient(required_rank: str, evidence_refs: list[str]) -> bool:
    """Check whether evidence refs satisfy a minimal rank requirement.

    Rank markers are expected in refs like ``rank:high::source`` or ``rank=medium``.
    Returns True when the best detected rank meets or exceeds ``required_rank``.
    Unranked evidence refs are treated as low-rank evidence.
    """
    required = _EVIDENCE_RANK_ORDER.get((required_rank or "").strip().lower(), 0)
    highest = 0
    for ref in evidence_refs:
        lower = (ref or "").strip().lower()
        for rank, score in _EVIDENCE_RANK_ORDER.items():
            token_forms = (f"rank:{rank}", f"rank={rank}", f"evidence_rank:{rank}", f"evidence_rank={rank}")
            if any(token in lower for token in token_forms):
                highest = max(highest, score)
    if highest == 0 and evidence_refs:
        highest = 1
    return highest >= required
