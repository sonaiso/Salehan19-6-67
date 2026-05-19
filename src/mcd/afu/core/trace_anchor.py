"""Typed trace anchors.

Every AFU artefact that can ever claim CERTIFICATE must trace back to a
concrete source: a raw input segment, a previously licensed output, or a
specific evidence record. ``TraceAnchor`` enforces that *at the leaf
level* before the value ever reaches a reverse-trace audit.

The taxonomy is intentionally small in PR 2. Later PRs may add anchor
kinds (e.g. ``proof_object``); the rule is that no kind may be silently
accepted — adding one requires updating :class:`TraceAnchorKind`.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from mcd.afu.contracts._common import AFUContractError


class TraceAnchorKind(str, Enum):
    INPUT_SEGMENT = "input_segment"
    EVIDENCE = "evidence"
    PRIOR_OUTPUT = "prior_output"
    GATE_VERDICT = "gate_verdict"


@dataclass(frozen=True)
class TraceAnchor:
    """A typed pointer back into the upstream of a stage.

    Fields:

    * ``kind`` — element of :class:`TraceAnchorKind` (never an unknown
      string).
    * ``locator`` — opaque, non-empty string the originating stage uses
      to find the anchor (offsets, hash, gate id, …).
    * ``summary`` — short human-readable description, mandatory so the
      anchor is auditable without re-fetching the source.
    """

    kind: TraceAnchorKind
    locator: str
    summary: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, TraceAnchorKind):
            try:
                object.__setattr__(self, "kind", TraceAnchorKind(self.kind))
            except (ValueError, TypeError) as exc:
                raise AFUContractError(
                    f"TraceAnchor.kind must be a TraceAnchorKind, got {self.kind!r}"
                ) from exc
        if not str(self.locator).strip():
            raise AFUContractError("TraceAnchor.locator must be non-empty")
        if not str(self.summary).strip():
            raise AFUContractError("TraceAnchor.summary must be non-empty")
        object.__setattr__(self, "locator", str(self.locator).strip())
        object.__setattr__(self, "summary", str(self.summary).strip())


__all__ = ["TraceAnchor", "TraceAnchorKind"]
