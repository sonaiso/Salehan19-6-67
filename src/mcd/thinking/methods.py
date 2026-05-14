"""Thinking method models and evidence-rank helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient

MethodType = Literal["rational", "scientific", "formal", "linguistic", "normative", "systemic"]
ThinkingEvidenceRank = Literal["none", "low", "medium", "high", "governed"]

_THINKING_TO_CORE_RANK: dict[str, EpistemicRank] = {
    "none": EpistemicRank.ZERO,
    "low": EpistemicRank.POSSIBILITY,
    "medium": EpistemicRank.HYPOTHESIS,
    "high": EpistemicRank.STRONG_EVIDENCE,
    # "governed" means certificate-eligible evidence rank, not certificate by itself.
    "governed": EpistemicRank.CERTIFICATE,
}
_CORE_RANK_TOKENS: dict[str, EpistemicRank] = {
    rank.name.lower(): rank
    for rank in EpistemicRank
    if rank not in {EpistemicRank.CERTIFICATE, EpistemicRank.FINAL_JUDGMENT}
}


def _build_rank_marker_forms(token: str) -> tuple[str, str, str, str]:
    """Build accepted rank marker variants for a rank token."""
    normalized = (token or "").strip().lower()
    return (
        f"rank:{normalized}",
        f"rank={normalized}",
        f"evidence_rank:{normalized}",
        f"evidence_rank={normalized}",
    )


@dataclass
class ThinkingMethod:
    method_id: str
    method_type: MethodType
    required_inputs: list[str]
    allowed_outputs: list[str]
    forbidden_outputs: list[str]
    required_evidence_rank: str = "medium"
    residual_policy: str = "preserve"


def thinking_rank_to_core_epistemic_rank(rank: str) -> EpistemicRank:
    """Map thinking/core rank token into a core EpistemicRank value."""
    normalized = (rank or "").strip().lower()
    if normalized in _THINKING_TO_CORE_RANK:
        return _THINKING_TO_CORE_RANK[normalized]
    if normalized in _CORE_RANK_TOKENS:
        return _CORE_RANK_TOKENS[normalized]
    return EpistemicRank.ZERO


def detect_highest_evidence_rank(evidence_refs: list[str]) -> EpistemicRank:
    """Return the highest core rank found in evidence refs.

    If refs exist but no explicit rank marker is present, this defaults to
    POSSIBILITY.
    """
    rank_markers: dict[str, EpistemicRank] = {
        **_THINKING_TO_CORE_RANK,
        **_CORE_RANK_TOKENS,
    }
    highest = EpistemicRank.ZERO
    for ref in evidence_refs:
        lower = (ref or "").strip().lower()
        for token, rank in rank_markers.items():
            token_forms = _build_rank_marker_forms(token)
            if any(marker in lower for marker in token_forms):
                highest = max(highest, rank)
    if highest == EpistemicRank.ZERO and evidence_refs:
        return EpistemicRank.POSSIBILITY
    return highest


def evidence_rank_sufficient(required_rank: str, evidence_refs: list[str]) -> bool:
    """Check whether evidence refs satisfy a minimal rank requirement.

    Supports both thinking-rank markers (none/low/medium/high/governed) and
    core epistemic rank markers (ZERO/POSSIBILITY/HYPOTHESIS/WEAK_EVIDENCE/
    STRONG_EVIDENCE/CERTIFICATE).
    Unranked evidence refs are treated as POSSIBILITY by
    ``detect_highest_evidence_rank``.
    """
    required = thinking_rank_to_core_epistemic_rank(required_rank)
    highest = detect_highest_evidence_rank(evidence_refs)
    return is_rank_sufficient(highest, required)
