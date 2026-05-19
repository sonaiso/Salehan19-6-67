"""Residual adapter for :mod:`mcd.afu.fractal_definition`.

The brief's §13 sketches a ``Residual`` dataclass with
``code / family / blocking / description`` fields. The existing
:class:`mcd.core.residual_taxonomy.ResidualSpec` already covers that
shape and more (severity, remediation hint, central registry). The
adapter here is a *thin* wrapper that:

* normalises a residual code through
  :func:`mcd.core.residual_taxonomy.classify_residual` — unknown codes
  are kept (no erasure) and flagged as blocking, exactly as the
  taxonomy already does;
* exposes the four brief-shape fields via properties so downstream
  code stays decoupled from the kernel taxonomy;
* refuses to be silently constructed from an empty code (which would
  invite the ``residual_erasure`` failure mode).
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu.contracts._common import AFUContractError
from mcd.core.residual_taxonomy import ResidualSpec, classify_residual


@dataclass(frozen=True)
class Residual:
    """Adapter over :class:`ResidualSpec` carrying the four brief fields."""

    code: str
    spec: ResidualSpec

    def __post_init__(self) -> None:
        if not str(self.code or "").strip():
            raise AFUContractError("Residual.code must be non-empty")
        cleaned = str(self.code).strip()
        spec = self.spec
        # Re-classify defensively to refuse a spec that contradicts the
        # provided code.
        canonical = classify_residual(cleaned)
        if not isinstance(spec, ResidualSpec) or spec.code != canonical.code:
            spec = canonical
        object.__setattr__(self, "code", cleaned)
        object.__setattr__(self, "spec", spec)

    # --- brief-shape projection -------------------------------------------------
    @property
    def family(self) -> str:
        return self.spec.family.value

    @property
    def blocking(self) -> bool:
        return bool(self.spec.blocks_certificate)

    @property
    def description(self) -> str:
        return self.spec.default_message

    @classmethod
    def of(cls, code: str) -> "Residual":
        """Build a :class:`Residual` purely from a code."""
        return cls(code=code, spec=classify_residual(code))


__all__ = ["Residual"]
