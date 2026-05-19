"""Forward / backward transition records.

A :class:`ForwardTransition` is the *plan* of how a definition is built
from prior state; a :class:`BackwardVerification` is the *plan* of how a
definition is tested from a later effect. Both are pure data — no
execution lives here; that belongs to
:class:`mcd.afu.fractal_definition.runtime.FractalDefinitionRuntime`.

The constructors enforce a small set of self-loops that the
constitution forbids by name:

* ``from_layer == to_layer`` → ``silent_level_skip`` by self-loop.
* empty ``gate_id`` → no anchor to the Gate Registry.
* unclassifiable residual code → silent residual erasure risk.
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu.contracts._common import AFUContractError, freeze_strings
from mcd.core.residual_taxonomy import classify_residual


def _nonempty(name: str, value: object) -> str:
    if not str(value or "").strip():
        raise AFUContractError(f"{name} must be non-empty")
    return str(value).strip()


def _validated_residuals(codes: tuple[str, ...]) -> tuple[str, ...]:
    cleaned = freeze_strings(codes)
    for code in cleaned:
        # classify_residual never raises; an unknown code is round-tripped
        # as a blocker. Calling it here forces the consumer to be aware
        # of unknown codes at construction time (the test suite asserts
        # that unknown codes are kept and remain blocking).
        classify_residual(code)
    return cleaned


@dataclass(frozen=True)
class ForwardTransition:
    """Plan for a forward (Φᵢ) step between two AFU layers."""

    from_layer: str
    to_layer: str
    gate_id: str
    expected_evidence_kinds: tuple[str, ...] = ()
    allowed_residuals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        from_layer = _nonempty("ForwardTransition.from_layer", self.from_layer)
        to_layer = _nonempty("ForwardTransition.to_layer", self.to_layer)
        if from_layer == to_layer:
            raise AFUContractError(
                "silent_level_skip: ForwardTransition cannot loop from a "
                f"layer to itself ({from_layer!r})"
            )
        gate_id = _nonempty("ForwardTransition.gate_id", self.gate_id)
        object.__setattr__(self, "from_layer", from_layer)
        object.__setattr__(self, "to_layer", to_layer)
        object.__setattr__(self, "gate_id", gate_id)
        object.__setattr__(
            self,
            "expected_evidence_kinds",
            freeze_strings(self.expected_evidence_kinds),
        )
        object.__setattr__(
            self,
            "allowed_residuals",
            _validated_residuals(tuple(self.allowed_residuals or ())),
        )


@dataclass(frozen=True)
class BackwardVerification:
    """Plan for a backward (reverse-trace) step from a probing layer."""

    target_layer: str
    probing_layer: str
    gate_id: str
    expected_anchor_kinds: tuple[str, ...] = ()
    downgrade_residuals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        target = _nonempty("BackwardVerification.target_layer", self.target_layer)
        probe = _nonempty("BackwardVerification.probing_layer", self.probing_layer)
        if target == probe:
            raise AFUContractError(
                "silent_level_skip: BackwardVerification cannot probe a "
                f"layer with itself ({target!r})"
            )
        gate_id = _nonempty("BackwardVerification.gate_id", self.gate_id)
        object.__setattr__(self, "target_layer", target)
        object.__setattr__(self, "probing_layer", probe)
        object.__setattr__(self, "gate_id", gate_id)
        object.__setattr__(
            self,
            "expected_anchor_kinds",
            freeze_strings(self.expected_anchor_kinds),
        )
        object.__setattr__(
            self,
            "downgrade_residuals",
            _validated_residuals(tuple(self.downgrade_residuals or ())),
        )


__all__ = ["BackwardVerification", "ForwardTransition"]
