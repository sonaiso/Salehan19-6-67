"""Non-destructive constructional-law witness.

:func:`is_fractal` re-runs every checkable §15 invariant against a
purported definition and returns ``(ok, reasons)`` instead of raising.
The test suite uses this to enumerate every individual failure mode
without having to ``pytest.raises`` over each one.

Calling :func:`is_fractal` on a *constructed* :class:`FractalDefinition`
should always return ``(True, ())`` because the constructor enforces
the same laws. Calling it on a dict-shaped dry-run (mapping of field
name to value) is useful at fixture-load time to produce a complete
failure list before construction even attempts.
"""
from __future__ import annotations

from typing import Mapping

from .template import FractalDefinition

_REQUIRED_SCALAR_FIELDS: tuple[str, ...] = (
    "name",
    "layer",
    "carrier",
    "domain",
    "function",
    "formation_gate",
    "backward_gate",
    "output_contract",
)


def _is_blank(value: object) -> bool:
    return not str(value or "").strip()


def is_fractal(definition: object) -> tuple[bool, tuple[str, ...]]:
    """Return ``(ok, reasons)``.

    Accepts either a :class:`FractalDefinition` instance (in which case
    the checks are trivially satisfied because the constructor enforces
    them) or a :class:`Mapping` shaped like the dataclass fields.
    """
    reasons: list[str] = []

    if isinstance(definition, FractalDefinition):
        # The constructor guarantees the invariants. The function still
        # walks the fields so tests can rely on a uniform interface.
        data: Mapping[str, object] = {
            name: getattr(definition, name) for name in _REQUIRED_SCALAR_FIELDS
        }
        data = {**data, "distinction": definition.distinction}
    elif isinstance(definition, Mapping):
        data = definition
    else:
        return False, (
            f"is_fractal: expected FractalDefinition or Mapping, got "
            f"{type(definition).__name__}",
        )

    for name in _REQUIRED_SCALAR_FIELDS:
        if _is_blank(data.get(name)):
            reasons.append(f"missing_or_empty:{name}")

    distinction = data.get("distinction") or ()
    if not isinstance(distinction, (list, tuple)) or not any(
        str(v or "").strip() for v in distinction
    ):
        reasons.append("missing_or_empty:distinction")

    return (not reasons, tuple(reasons))


__all__ = ["is_fractal"]
