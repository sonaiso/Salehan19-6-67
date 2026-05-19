"""Monotone bind for :class:`LicensedOutput`.

The architectural law for the AFU spine is

    Φᵢ(Sᵢ) = Sᵢ₊₁

where each stage emits a :class:`LicensedOutput`. Composing two stages
must obey three properties, *all enforced by this function*:

1. **Rank monotonicity** — the composite rank is the meet of the inputs;
   no composition can elevate confidence.
2. **Residual preservation** — every residual code from any input
   appears in the composite (no ``residual_erasure``).
3. **Gate / evidence union** — selected gates and evidence anchors are
   the deduplicating union, preserving first-seen order, so the audit
   trail is monotone and reproducible.

This is the *only* sanctioned way to combine licensed outputs inside
AFU. Stages must not roll their own composition.
"""
from __future__ import annotations

from mcd.afu.contracts._common import LicensedOutput

from .rank_lattice import cap_by_residuals, meet_ranks
from .residual_vector import accumulate_residuals


def _union(*tuples: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for t in tuples:
        for item in t:
            if item not in seen:
                seen.add(item)
                out.append(item)
    return tuple(out)


def bind_licensed(left: LicensedOutput, right: LicensedOutput) -> LicensedOutput:
    """Compose two licensed outputs under the AFU law.

    Implementation notes:

    * ``rank`` is :func:`meet_ranks` of both inputs, then capped through
      :func:`cap_by_residuals` against the merged residual vector.
    * ``residuals`` are merged with :func:`accumulate_residuals` so the
      union is order-preserving and duplicate-free.
    * ``selected_gates`` and ``evidence`` are unioned with first-seen
      order so the resulting audit is stable under associativity.
    """
    if not isinstance(left, LicensedOutput) or not isinstance(right, LicensedOutput):
        raise TypeError("bind_licensed expects two LicensedOutput instances")

    residuals = accumulate_residuals(left.residuals, right.residuals)
    rank = cap_by_residuals(meet_ranks(left.rank, right.rank), residuals)
    return LicensedOutput(
        selected_gates=_union(left.selected_gates, right.selected_gates),
        evidence=_union(left.evidence, right.evidence),
        residuals=residuals,
        rank=rank,
    )


__all__ = ["bind_licensed"]
