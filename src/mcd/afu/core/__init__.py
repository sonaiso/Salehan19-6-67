"""AFU core algebra.

These modules are the *substrate* on which :mod:`mcd.afu.fractal_definition`
stands. They are deliberately small and side-effect free:

* :mod:`rank_lattice` — public lattice ZERO ⊑ HYPOTHESIS ⊑ CERTIFICATE with
  ``meet`` / ``join`` / ``cap_by_residuals``.
* :mod:`residual_vector` — order-preserving, deduplicating residual code
  accumulator.
* :mod:`gate` — the ``Gate`` / ``GateSpec`` / ``GateVerdict`` primitive
  consumed by every future stage.
* :mod:`trace_anchor` — typed anchors pointing back into the raw prompt or
  a previously licensed output.
* :mod:`licensed_bind` — monotone composition for :class:`LicensedOutput`.

No layer-specific concept (حرف, جذر, دال, حكم, …) is allowed in this
sub-package. The algebra is universal.
"""
from __future__ import annotations

from .gate import Gate, GateSpec, GateStatus, GateVerdict
from .licensed_bind import bind_licensed
from .rank_lattice import cap_by_residuals, join_ranks, meet_ranks
from .residual_vector import accumulate_residuals
from .trace_anchor import TraceAnchor, TraceAnchorKind

__all__ = [
    "Gate",
    "GateSpec",
    "GateStatus",
    "GateVerdict",
    "TraceAnchor",
    "TraceAnchorKind",
    "accumulate_residuals",
    "bind_licensed",
    "cap_by_residuals",
    "join_ranks",
    "meet_ranks",
]
