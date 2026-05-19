"""Residual vector accumulator.

Residuals are *evidence-of-incompleteness*. They must never be silently
erased (``residual_erasure`` is a forbidden transition). This module
gives stages a single, order-preserving, deduplicating accumulator so
that combining residual vectors from multiple sources is associative,
commutative-under-set-semantics, and idempotent.
"""
from __future__ import annotations

from typing import Iterable


def _clean(codes: Iterable[str] | None) -> Iterable[str]:
    if codes is None:
        return ()
    for c in codes:
        s = str(c or "").strip()
        if s:
            yield s


def accumulate_residuals(*vectors: Iterable[str] | None) -> tuple[str, ...]:
    """Merge residual code vectors preserving first-seen order.

    Properties (witnessed by tests in
    ``tests/afu/core/test_residual_vector.py``):

    * **No erasure** — every non-empty code in any input vector appears
      in the output.
    * **Order-preserving** — codes appear in their first-seen position.
    * **Idempotent** — ``accumulate_residuals(v, v) == accumulate_residuals(v)``.
    * **Associative** under set semantics.
    """
    seen: set[str] = set()
    out: list[str] = []
    for v in vectors:
        for code in _clean(v):
            if code not in seen:
                seen.add(code)
                out.append(code)
    return tuple(out)


__all__ = ["accumulate_residuals"]
