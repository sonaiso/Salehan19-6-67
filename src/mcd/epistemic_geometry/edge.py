from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MinimalFractalEdge:
    edge_id: str
    source_node: str
    target_node: str
    morphism_id: str
    relation_type: str
    preserves: list[str] = field(default_factory=list)
    adds: list[str] = field(default_factory=list)
    forbids: list[str] = field(default_factory=list)
    gate_requirements: dict[str, int] = field(default_factory=dict)
    score_effects: dict[str, float] = field(default_factory=dict)
    residual_policy: dict[str, str] = field(default_factory=dict)
    trace_policy: dict[str, str] = field(default_factory=dict)
    level_step: int = 1

    def __post_init__(self) -> None:
        if not self.edge_id:
            raise ValueError("edge_id is required")
        if not self.source_node or not self.target_node:
            raise ValueError("source_node and target_node are required")
        if self.level_step < 1:
            raise ValueError("level_step must be >= 1")

