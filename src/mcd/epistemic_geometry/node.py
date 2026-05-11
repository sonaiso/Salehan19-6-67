from __future__ import annotations

from dataclasses import dataclass, field

from .dimension import EpistemicDimension

FINAL_JUDGMENTS: set[str] = {"ZERO", "HYPOTHESIS", "CERTIFICATE"}


@dataclass
class MinimalFractalNode:
    node_id: str
    rank: int
    node_type: str
    domain: str
    dimensions: list[EpistemicDimension] = field(default_factory=list)
    gates: dict[str, int] = field(default_factory=dict)
    scores: dict[str, float] = field(default_factory=dict)
    relations: list[dict[str, str]] = field(default_factory=list)
    incoming_edges: list[str] = field(default_factory=list)
    outgoing_edges: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    allowed_next: list[str] = field(default_factory=list)
    forbidden_transitions: list[str] = field(default_factory=list)
    judgment: str = "HYPOTHESIS"

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if self.rank < 0:
            raise ValueError("rank must be >= 0")
        if not self.node_type:
            raise ValueError("node_type is required")
        if self.judgment not in FINAL_JUDGMENTS:
            raise ValueError(f"judgment must be one of {sorted(FINAL_JUDGMENTS)}")

