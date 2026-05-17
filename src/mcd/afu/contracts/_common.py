"""Shared primitives for AFU contracts.

This module is the *only* place where AFU contracts touch the existing
governance kernel. Each contract built on top of these primitives stays
purely declarative: contracts hold data and validate their own shape;
they never execute theory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from mcd.core.epistemic_rank import EpistemicRank, parse_rank
from mcd.core.residual_taxonomy import (
    ResidualSpec,
    classify_residual,
    has_blocking_residuals,
)

#: Public rank labels valid for AFU contracts. Mirrors the constitutional
#: lattice ZERO / HYPOTHESIS / CERTIFICATE — no fourth final status.
ALLOWED_PUBLIC_RANKS: frozenset[EpistemicRank] = frozenset(
    {EpistemicRank.ZERO, EpistemicRank.HYPOTHESIS, EpistemicRank.CERTIFICATE}
)


class AFUContractError(ValueError):
    """Raised when an AFU contract is constructed in an invalid shape.

    The error is fail-closed by design: any violation downgrades the
    contract rather than silently allowing an upgrade.
    """


def normalize_rank(rank: EpistemicRank | str) -> EpistemicRank:
    """Parse and constrain a rank to AFU's public lattice.

    Internal kernel ranks (POSSIBILITY/WEAK/STRONG/FINAL_JUDGMENT) are
    not legal final statuses for AFU contracts and are clamped to
    HYPOTHESIS rather than silently elevated.
    """
    parsed = parse_rank(rank)
    if parsed not in ALLOWED_PUBLIC_RANKS:
        return EpistemicRank.HYPOTHESIS
    return parsed


def freeze_strings(values: Iterable[str] | None) -> tuple[str, ...]:
    """Return an immutable tuple of stripped, non-empty strings."""
    if values is None:
        return ()
    out: list[str] = []
    for v in values:
        s = str(v).strip()
        if s:
            out.append(s)
    return tuple(out)


def freeze_residuals(codes: Iterable[str] | None) -> tuple[str, ...]:
    """Freeze residual codes as a tuple. Codes are *not* silently
    re-classified; the caller (or a stage) is responsible for sourcing
    codes from :mod:`mcd.core.residual_taxonomy`. Unknown codes will be
    flagged as blocking by ``classify_residual`` at audit time.
    """
    return freeze_strings(codes)


def classify(codes: Iterable[str]) -> tuple[ResidualSpec, ...]:
    """Convenience wrapper around :func:`classify_residual`."""
    return tuple(classify_residual(c) for c in codes)


def residuals_block_certificate(codes: Iterable[str]) -> bool:
    """Return True when any residual blocks certificate emission."""
    return has_blocking_residuals(tuple(codes))


@dataclass(frozen=True)
class TraceStep:
    """One step in the AFU pipeline reverse trace.

    Each step records *which* stage emitted it, *which* gates from the
    Gate Registry were selected (PR 1: usually empty — the registry is
    introduced in PR 3), and an evidence anchor pointing back into the
    raw prompt or a previously licensed output.
    """

    stage: str
    summary: str
    selected_gates: tuple[str, ...] = ()
    evidence_anchor: str = ""

    def __post_init__(self) -> None:
        if not str(self.stage).strip():
            raise AFUContractError("TraceStep.stage must be non-empty")
        if not str(self.summary).strip():
            raise AFUContractError("TraceStep.summary must be non-empty")
        # Normalize selected_gates into a frozen tuple of clean strings.
        object.__setattr__(self, "selected_gates", freeze_strings(self.selected_gates))


@dataclass(frozen=True)
class LicensedOutput:
    """The minimal envelope for any AFU stage output.

    Mathematical shape (from the architectural brief)::

        Φᵢ(x) = License(
            Outputᵢ(x),
            SelectedGatesᵢ(x),
            Evidenceᵢ(x),
            Residualsᵢ(x),
            Rankᵢ(x),
        )

    ``SelectedGates`` is a subset of the (future) Gate Registry — never
    the whole theory. ``rank`` is constrained to the public lattice and
    is downgraded if blocking residuals are present.
    """

    selected_gates: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS

    def __post_init__(self) -> None:
        object.__setattr__(self, "selected_gates", freeze_strings(self.selected_gates))
        object.__setattr__(self, "evidence", freeze_strings(self.evidence))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        # Fail-closed: a blocking residual cannot coexist with a
        # CERTIFICATE rank. This blocks `certificate_with_blocking_residuals`
        # at construction time rather than leaving it to a later audit.
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)


__all__ = [
    "AFUContractError",
    "ALLOWED_PUBLIC_RANKS",
    "EpistemicRank",
    "LicensedOutput",
    "TraceStep",
    "classify",
    "freeze_residuals",
    "freeze_strings",
    "normalize_rank",
    "residuals_block_certificate",
]
