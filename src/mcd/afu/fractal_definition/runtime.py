"""Runtime twin of :class:`FractalDefinition` (§14 of the brief).

§14: every fractal definition must expose two functions —
``forward_define`` (build from prior state) and ``backward_verify``
(probe from a later effect). Neither is sufficient on its own.

This module ships the abstract :class:`FractalDefinitionRuntime` and a
concrete fail-closed default :class:`NullFractalRuntime` so unfinished
layers are *legal but capped at HYPOTHESIS* — they can never silently
elevate to CERTIFICATE because the registry is empty and the residual
``unknown_gate`` is blocking.
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu.contracts._common import (
    AFUContractError,
    EpistemicRank,
    LicensedOutput,
)

from ..core.rank_lattice import cap_by_residuals
from ..core.residual_vector import accumulate_residuals
from .residual import Residual
from .template import FractalDefinition


@dataclass(frozen=True)
class FractalDefinitionRuntime:
    """Abstract runtime bound to a :class:`FractalDefinition`.

    Subclasses MUST override both :meth:`forward_define` and
    :meth:`backward_verify`. The base methods raise
    :class:`NotImplementedError` deliberately — the §14 statement
    *"forward alone is insufficient"* is enforced by absence of a usable
    default, not by silent stubs.
    """

    definition: FractalDefinition

    def __post_init__(self) -> None:
        if not isinstance(self.definition, FractalDefinition):
            raise AFUContractError(
                "FractalDefinitionRuntime.definition must be a FractalDefinition"
            )

    def forward_define(self, prior_state: object) -> LicensedOutput:
        """Build the unit from prior state via :attr:`definition.formation_gate`."""
        raise NotImplementedError(
            "FractalDefinitionRuntime subclasses must implement forward_define"
        )

    def backward_verify(self, later_effect: object) -> EpistemicRank:
        """Probe the unit from a later effect via :attr:`definition.backward_gate`."""
        raise NotImplementedError(
            "FractalDefinitionRuntime subclasses must implement backward_verify"
        )


def _residual_codes_from_effect(later_effect: object) -> tuple[str, ...]:
    """Best-effort extraction of residual codes from an opaque effect."""
    if later_effect is None:
        return ()
    if isinstance(later_effect, LicensedOutput):
        return tuple(later_effect.residuals)
    if isinstance(later_effect, dict):
        raw = later_effect.get("residuals") or ()
        codes: list[str] = []
        for item in raw:
            if isinstance(item, Residual):
                codes.append(item.code)
            else:
                s = str(item or "").strip()
                if s:
                    codes.append(s)
        return tuple(codes)
    return ()


@dataclass(frozen=True)
class NullFractalRuntime(FractalDefinitionRuntime):
    """Fail-closed default runtime.

    * :meth:`forward_define` returns a :class:`LicensedOutput` with
      ``rank=HYPOTHESIS``, the definition's ``formation_gate`` recorded
      in ``selected_gates``, the definition's residuals merged with the
      blocking ``unknown_gate`` residual.
    * :meth:`backward_verify` returns :class:`EpistemicRank.HYPOTHESIS`
      unless ``later_effect`` carries any blocking residual code, in
      which case it returns :class:`EpistemicRank.ZERO`.

    The result is that a layer which has not yet supplied a real runtime
    is still wired into the spine — but cannot certify anything.
    """

    def forward_define(self, prior_state: object) -> LicensedOutput:
        definition = self.definition
        residuals = accumulate_residuals(
            definition.residual_codes(), ("unknown_gate",)
        )
        # Build evidence in the LicensedOutput sense: a deterministic
        # textual trace of the definition's evidence records.
        evidence = definition.evidence_summaries()
        rank = cap_by_residuals(EpistemicRank.HYPOTHESIS, residuals)
        return LicensedOutput(
            selected_gates=(definition.formation_gate,),
            evidence=evidence,
            residuals=residuals,
            rank=rank,
        )

    def backward_verify(self, later_effect: object) -> EpistemicRank:
        codes = _residual_codes_from_effect(later_effect)
        # A blocking residual collapses the verification to ZERO.
        # Otherwise the verification remains an open hypothesis — never
        # CERTIFICATE, because no real evaluator has run.
        capped = cap_by_residuals(EpistemicRank.CERTIFICATE, codes)
        if capped < EpistemicRank.HYPOTHESIS:
            return EpistemicRank.ZERO
        if codes:
            # If we received residuals at all, *any* known blocker
            # collapses to ZERO; otherwise we remain in HYPOTHESIS.
            from mcd.core.residual_taxonomy import classify_residual

            for code in codes:
                if classify_residual(code).blocks_certificate:
                    return EpistemicRank.ZERO
        return EpistemicRank.HYPOTHESIS


__all__ = ["FractalDefinitionRuntime", "NullFractalRuntime"]
