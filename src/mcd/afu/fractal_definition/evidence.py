"""Evidence adapter for :mod:`mcd.afu.fractal_definition`.

The §13 brief sketches ``Evidence(source, claim, strength)``. The
fractal-definition layer additionally requires that any
``strength == CERTIFICATE`` evidence carries a backing
:class:`TraceAnchor` whose kind is one of
``INPUT_SEGMENT`` or ``EVIDENCE``. Without that anchor the leaf would
violate the constitutional ``certificate_without_reverse_trace``
forbidden transition.
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu.contracts._common import AFUContractError, EpistemicRank

from ..core.trace_anchor import TraceAnchor, TraceAnchorKind
from .rank import normalize_rank

_CERTIFICATE_ANCHOR_KINDS: frozenset[TraceAnchorKind] = frozenset(
    {TraceAnchorKind.INPUT_SEGMENT, TraceAnchorKind.EVIDENCE}
)


@dataclass(frozen=True)
class Evidence:
    """A single evidence record attached to a :class:`FractalDefinition`.

    Fields:

    * ``source`` — non-empty string identifying *where* the evidence
      comes from (e.g. ``"raw_prompt"``, ``"licensed_output:linker"``).
    * ``claim`` — non-empty string stating *what* the evidence supports.
    * ``strength`` — public-lattice rank (clamped through
      :func:`normalize_rank`); CERTIFICATE requires an anchor.
    * ``anchor`` — optional :class:`TraceAnchor`. Mandatory when
      ``strength == CERTIFICATE``.
    """

    source: str
    claim: str
    strength: EpistemicRank = EpistemicRank.HYPOTHESIS
    anchor: TraceAnchor | None = None

    def __post_init__(self) -> None:
        if not str(self.source or "").strip():
            raise AFUContractError("Evidence.source must be non-empty")
        if not str(self.claim or "").strip():
            raise AFUContractError("Evidence.claim must be non-empty")
        object.__setattr__(self, "source", str(self.source).strip())
        object.__setattr__(self, "claim", str(self.claim).strip())

        strength = normalize_rank(self.strength)
        if strength == EpistemicRank.CERTIFICATE:
            if not isinstance(self.anchor, TraceAnchor):
                raise AFUContractError(
                    "certificate_without_reverse_trace: Evidence with "
                    "strength=CERTIFICATE requires a TraceAnchor"
                )
            if self.anchor.kind not in _CERTIFICATE_ANCHOR_KINDS:
                raise AFUContractError(
                    "certificate_without_reverse_trace: Evidence with "
                    "strength=CERTIFICATE requires an anchor of kind "
                    "input_segment or evidence; got "
                    f"{self.anchor.kind.value}"
                )
        object.__setattr__(self, "strength", strength)


__all__ = ["Evidence"]
