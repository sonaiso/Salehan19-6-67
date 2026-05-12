"""Rank calculus utilities for linking governance."""
from __future__ import annotations

from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient, parse_rank, required_rank_for_judgment
from mcd.core.linking_type import LinkingType, parse_linking_type


class RankCalculationError(ValueError):
    """Raised when rank calculus constraints are violated."""


LINKING_MIN_EVIDENCE_RANK: dict[LinkingType, EpistemicRank] = {
    LinkingType.SYMBOLIC: EpistemicRank.ZERO,
    LinkingType.SEMANTIC: EpistemicRank.HYPOTHESIS,
    LinkingType.CONTEXTUAL: EpistemicRank.WEAK_EVIDENCE,
    LinkingType.CAUSAL: EpistemicRank.STRONG_EVIDENCE,
    LinkingType.INTERPRETIVE: EpistemicRank.HYPOTHESIS,
    LinkingType.EVIDENTIARY: EpistemicRank.STRONG_EVIDENCE,
    LinkingType.GOVERNED_CERTIFICATION: EpistemicRank.CERTIFICATE,
}


FINAL_JUDGMENTS = {"ZERO", "HYPOTHESIS", "CERTIFICATE"}


def minimum_evidence_rank_for_link(linking_type: LinkingType | str) -> EpistemicRank:
    return LINKING_MIN_EVIDENCE_RANK[parse_linking_type(linking_type)]


def rank_at_least(actual_rank: EpistemicRank | str, required_rank: EpistemicRank | str) -> bool:
    return is_rank_sufficient(actual_rank, required_rank)


def enforce_linking_rank(linking_type: LinkingType | str, evidence_rank: EpistemicRank | str) -> None:
    minimum = minimum_evidence_rank_for_link(linking_type)
    if not rank_at_least(evidence_rank, minimum):
        raise RankCalculationError(
            f"insufficient evidence rank for {parse_linking_type(linking_type).name}: "
            f"{parse_rank(evidence_rank).name} < {minimum.name}"
        )


def enforce_judgment_rank(evidence_rank: EpistemicRank | str, judgment: str) -> None:
    required = required_rank_for_judgment(judgment)
    if not rank_at_least(evidence_rank, required):
        raise RankCalculationError(
            f"insufficient evidence rank for judgment {judgment}: "
            f"{parse_rank(evidence_rank).name} < {required.name}"
        )


def downgrade_judgment_for_residuals(judgment: str, residuals: list[str] | None) -> str:
    normalized = (judgment or "").strip().upper()
    if normalized not in FINAL_JUDGMENTS:
        return normalized
    if not residuals:
        return normalized
    if normalized == "CERTIFICATE":
        return "HYPOTHESIS"
    if normalized == "HYPOTHESIS":
        return "ZERO"
    return "ZERO"
