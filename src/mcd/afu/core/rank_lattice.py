"""Public rank lattice for AFU.

The constitution allows only three final epistemic statuses:

    ZERO ⊑ HYPOTHESIS ⊑ CERTIFICATE

Internal kernel ranks (POSSIBILITY / WEAK_EVIDENCE / STRONG_EVIDENCE /
FINAL_JUDGMENT) are *not* public statuses; any value that does not lie on
the public lattice is folded down to HYPOTHESIS rather than silently
elevated. This module provides the lattice operations every AFU stage
needs to compose ranks safely.
"""
from __future__ import annotations

from typing import Iterable

from mcd.afu.contracts._common import (
    ALLOWED_PUBLIC_RANKS,
    EpistemicRank,
    normalize_rank,
    residuals_block_certificate,
)


def _public(rank: EpistemicRank | str) -> EpistemicRank:
    """Project ``rank`` onto the public lattice."""
    return normalize_rank(rank)


def meet_ranks(*ranks: EpistemicRank | str) -> EpistemicRank:
    """Return the greatest lower bound of ``ranks`` on the public lattice.

    The meet is fail-closed: with no inputs the meet is ZERO; the meet of
    a non-public rank with anything is at most HYPOTHESIS. This is the
    same operation :class:`LicensedResponse` already uses to combine
    component-stage ranks.
    """
    if not ranks:
        return EpistemicRank.ZERO
    folded = [int(_public(r)) for r in ranks]
    return EpistemicRank(min(folded))


def join_ranks(*ranks: EpistemicRank | str) -> EpistemicRank:
    """Return the least upper bound of ``ranks`` on the public lattice.

    Join is used only when explicitly accumulating *evidence in favour of
    the same claim*. It still never returns a non-public rank.
    """
    if not ranks:
        return EpistemicRank.ZERO
    folded = [int(_public(r)) for r in ranks]
    return EpistemicRank(max(folded))


def cap_by_residuals(
    rank: EpistemicRank | str, residual_codes: Iterable[str]
) -> EpistemicRank:
    """Cap ``rank`` at HYPOTHESIS when any residual blocks certification.

    This mirrors :class:`LicensedOutput`'s post-init guard so the same
    fail-closed rule can be invoked from non-contract call sites (gate
    evaluators, runtime stages, the fractal-definition template, …).
    """
    public = _public(rank)
    codes = tuple(residual_codes or ())
    if public == EpistemicRank.CERTIFICATE and residuals_block_certificate(codes):
        return EpistemicRank.HYPOTHESIS
    return public


__all__ = [
    "ALLOWED_PUBLIC_RANKS",
    "cap_by_residuals",
    "join_ranks",
    "meet_ranks",
]
