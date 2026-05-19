"""Rank adapter for :mod:`mcd.afu.fractal_definition`.

The brief's §13 proposes a four-level ``Rank`` enum
(ZERO / HYPOTHESIS / LICENSED / CERTIFICATE). The constitution forbids a
fourth final epistemic status: only ZERO, HYPOTHESIS, and CERTIFICATE
are legal terminal judgments. We resolve this here by:

* **Re-exporting** :class:`EpistemicRank` under the alias :data:`Rank`
  so the fractal-definition layer can speak the same vocabulary as the
  brief without inventing a parallel type.
* **Refusing** to introduce a ``LICENSED`` member. Licensure is a
  property of a :class:`LicensedOutput`, not a rank, and the existing
  envelope already carries it.
* Providing :func:`assert_public`, a strict version of
  :func:`normalize_rank` that raises :class:`AFUContractError` instead
  of silently clamping. The clamp form is appropriate for shaping
  inputs from upstream callers; the strict form is appropriate when an
  AFU module wants to refuse to even consider an internal kernel rank.
"""
from __future__ import annotations

from mcd.afu.contracts._common import (
    AFUContractError,
    ALLOWED_PUBLIC_RANKS,
    EpistemicRank,
    normalize_rank,
)

#: Public alias used by :mod:`mcd.afu.fractal_definition`.
Rank = EpistemicRank


def assert_public(rank: EpistemicRank | str) -> EpistemicRank:
    """Strict variant of :func:`normalize_rank`.

    Raises :class:`AFUContractError` if ``rank`` is not already a
    member of the public lattice ZERO/HYPOTHESIS/CERTIFICATE.
    """
    if isinstance(rank, EpistemicRank):
        parsed = rank
    else:
        try:
            parsed = EpistemicRank[str(rank or "").strip().upper()]
        except KeyError as exc:
            raise AFUContractError(
                f"rank {rank!r} is not on the public lattice "
                "(ZERO/HYPOTHESIS/CERTIFICATE)"
            ) from exc
    if parsed not in ALLOWED_PUBLIC_RANKS:
        raise AFUContractError(
            f"rank {parsed.name} is an internal kernel rank, not a public "
            "final status; use ZERO, HYPOTHESIS or CERTIFICATE."
        )
    return parsed


__all__ = [
    "ALLOWED_PUBLIC_RANKS",
    "AFUContractError",
    "EpistemicRank",
    "Rank",
    "assert_public",
    "normalize_rank",
]
