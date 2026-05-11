from __future__ import annotations

from dataclasses import dataclass, field

DIMENSION_TYPES: set[str] = {
    "existence",
    "trace",
    "distinction",
    "designation",
    "identity",
    "universal_particular",
    "domain",
    "aspect",
    "time",
    "judgment_rank",
    "relation",
    "evidence",
    "certainty",
    "residual",
    "reverse_trace",
    "governance",
}


@dataclass
class EpistemicDimension:
    dimension_id: str
    dimension_type: str
    gate: int
    score: float
    residuals: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    critical: bool = False

    def __post_init__(self) -> None:
        if not self.dimension_id:
            raise ValueError("dimension_id is required")
        if self.dimension_type not in DIMENSION_TYPES:
            raise ValueError(f"dimension_type must be one of {sorted(DIMENSION_TYPES)}")
        if self.gate not in (0, 1):
            raise ValueError("gate must be 0 or 1")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("score must be between 0 and 1")

