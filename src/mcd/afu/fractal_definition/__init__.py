"""Fractal Definition — the *definition-of-definition* contract.

This sub-package lands the universal 15-field template that every future
AFU layer (phonological, morphological, semantic, syntactic, normative,
…) must instantiate. No layer-specific concept (حرف, جذر, دال, حكم, …)
is introduced here. The brief's six worked examples live only as YAML
fixtures under ``tests/afu/fractal_definition/fixtures/``.

The two laws that everything else inherits from this PR:

* **Constructional law (§15 of the brief)**: no
  :class:`FractalDefinition` may be constructed without a non-empty
  ``formation_gate`` *and* a non-empty ``backward_gate``.
* **Runtime law (§14 of the brief)**: every
  :class:`FractalDefinitionRuntime` exposes ``forward_define`` and
  ``backward_verify``; ``forward_define`` alone is insufficient.

The constitution permits only three final epistemic statuses (ZERO /
HYPOTHESIS / CERTIFICATE). The brief's proposed fourth value
``Rank.LICENSED`` is deliberately *not* added — licensure is a property
of an output (already encoded by :class:`LicensedOutput`), not a fourth
final rank. See :mod:`mcd.afu.fractal_definition.rank` and
``docs/AFU_FRACTAL_DEFINITION.md`` for the rationale.
"""
from __future__ import annotations

from .evidence import Evidence
from .rank import Rank, assert_public, normalize_rank
from .residual import Residual
from .runtime import FractalDefinitionRuntime, NullFractalRuntime
from .template import FractalDefinition
from .transitions import BackwardVerification, ForwardTransition
from .validator import is_fractal

__all__ = [
    "BackwardVerification",
    "Evidence",
    "ForwardTransition",
    "FractalDefinition",
    "FractalDefinitionRuntime",
    "NullFractalRuntime",
    "Rank",
    "Residual",
    "assert_public",
    "is_fractal",
    "normalize_rank",
]
