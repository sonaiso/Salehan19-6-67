"""Formal epistemic rank system."""
from __future__ import annotations

from enum import IntEnum


class EpistemicRank(IntEnum):
    ZERO = 0
    POSSIBILITY = 1
    HYPOTHESIS = 2
    WEAK_EVIDENCE = 3
    STRONG_EVIDENCE = 4
    CERTIFICATE = 5
    FINAL_JUDGMENT = 6


def parse_rank(rank: str | EpistemicRank) -> EpistemicRank:
    if isinstance(rank, EpistemicRank):
        return rank
    normalized = (rank or "").strip().upper()
    return EpistemicRank[normalized]


def is_rank_sufficient(evidence_rank: str | EpistemicRank, required_rank: str | EpistemicRank) -> bool:
    return parse_rank(evidence_rank) >= parse_rank(required_rank)


def required_rank_for_judgment(judgment: str) -> EpistemicRank:
    normalized = (judgment or "").strip().upper()
    if normalized == "ZERO":
        return EpistemicRank.ZERO
    if normalized == "HYPOTHESIS":
        return EpistemicRank.HYPOTHESIS
    if normalized == "CERTIFICATE":
        return EpistemicRank.CERTIFICATE
    raise ValueError(f"unsupported final judgment: {judgment}")
