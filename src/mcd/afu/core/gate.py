"""Gate primitive — the atomic predicate of the AFU theory.

A :class:`Gate` is the smallest unit of *executed theory*: a named
predicate over some upstream state that produces a :class:`GateVerdict`
(rank, residuals, evidence). The Gate Registry (see
:mod:`mcd.afu.registry.gate_registry`) maps stable gate identifiers to
:class:`Gate` instances. In PR 2 the registry ships empty: any call to
``registry.evaluate`` returns the fail-closed verdict produced by
:func:`unknown_gate_verdict`.

Nothing in this module imports a theory layer (mantuq, mafhum, qiyas,
…). Concrete predicates land in later PRs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from mcd.afu.contracts._common import (
    AFUContractError,
    EpistemicRank,
    freeze_strings,
    normalize_rank,
)

from .rank_lattice import cap_by_residuals


class GateStatus(str, Enum):
    """Outcome of evaluating a gate.

    Distinct from :class:`EpistemicRank` because the *evaluation* itself
    can fail (``UNKNOWN``) without that meaning the underlying claim is
    false. ``UNKNOWN`` always produces a blocking residual.
    """

    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GateSpec:
    """Static description of a gate, separable from its evaluator.

    A ``GateSpec`` is what reviewers read; a ``Gate`` is what the runtime
    executes. The split lets us load specs from YAML in early PRs
    without committing executable code.
    """

    gate_id: str
    layer: str
    description: str
    expected_evidence_kinds: tuple[str, ...] = ()
    possible_residuals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("gate_id", "layer", "description"):
            value = getattr(self, name)
            if not str(value or "").strip():
                raise AFUContractError(f"GateSpec.{name} must be non-empty")
            object.__setattr__(self, name, str(value).strip())
        object.__setattr__(
            self,
            "expected_evidence_kinds",
            freeze_strings(self.expected_evidence_kinds),
        )
        object.__setattr__(
            self, "possible_residuals", freeze_strings(self.possible_residuals)
        )


@dataclass(frozen=True)
class GateVerdict:
    """Result of evaluating a gate.

    ``rank`` is folded through :func:`cap_by_residuals` so a verdict can
    never report CERTIFICATE while also carrying a blocking residual.
    """

    gate_id: str
    status: GateStatus
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    residuals: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        if not str(self.gate_id or "").strip():
            raise AFUContractError("GateVerdict.gate_id must be non-empty")
        object.__setattr__(self, "gate_id", str(self.gate_id).strip())
        if not isinstance(self.status, GateStatus):
            try:
                object.__setattr__(self, "status", GateStatus(self.status))
            except (ValueError, TypeError) as exc:
                raise AFUContractError(
                    f"GateVerdict.status must be a GateStatus, got {self.status!r}"
                ) from exc
        object.__setattr__(self, "residuals", freeze_strings(self.residuals))
        object.__setattr__(self, "evidence", freeze_strings(self.evidence))
        object.__setattr__(self, "note", str(self.note or "").strip())

        rank = normalize_rank(self.rank)
        # An UNKNOWN evaluation cannot license a CERTIFICATE.
        if self.status == GateStatus.UNKNOWN and rank == EpistemicRank.CERTIFICATE:
            rank = EpistemicRank.HYPOTHESIS
        # A FAILED evaluation collapses to ZERO regardless of input rank.
        if self.status == GateStatus.FAILED:
            rank = EpistemicRank.ZERO
        rank = cap_by_residuals(rank, self.residuals)
        object.__setattr__(self, "rank", rank)


GateEvaluator = Callable[[object], GateVerdict]
"""Signature every concrete gate evaluator must satisfy."""


@dataclass(frozen=True)
class Gate:
    """A named predicate: ``spec`` + an opaque evaluator.

    The evaluator is *not* invoked here — :class:`Gate` is pure data so
    it stays auditable. The :mod:`mcd.afu.registry` module is the only
    place evaluators are dispatched.
    """

    spec: GateSpec
    evaluator: GateEvaluator | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.spec, GateSpec):
            raise AFUContractError("Gate.spec must be a GateSpec")


def unknown_gate_verdict(gate_id: str) -> GateVerdict:
    """Standard fail-closed verdict for an unregistered gate."""
    return GateVerdict(
        gate_id=gate_id or "<unknown>",
        status=GateStatus.UNKNOWN,
        rank=EpistemicRank.HYPOTHESIS,
        residuals=("unknown_gate",),
        note="Gate is not registered in the Gate Registry.",
    )


__all__ = [
    "Gate",
    "GateEvaluator",
    "GateSpec",
    "GateStatus",
    "GateVerdict",
    "unknown_gate_verdict",
]
