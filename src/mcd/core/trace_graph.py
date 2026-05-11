"""Transition trace graph primitives for replay/reverse/audit."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TraceStep:
    name: str
    payload_ref: str = ""


@dataclass
class TraceGraph:
    steps: list[TraceStep] = field(default_factory=list)

    @classmethod
    def canonical(cls) -> "TraceGraph":
        return cls(
            steps=[
                TraceStep("Reality"),
                TraceStep("Linking"),
                TraceStep("Interpretation"),
                TraceStep("Evidence"),
                TraceStep("Governance"),
                TraceStep("Judgment"),
            ]
        )

    def replay(self) -> list[str]:
        return [s.name for s in self.steps]

    def reverse_trace(self) -> list[str]:
        return [s.name for s in reversed(self.steps)]

    def audit(self) -> dict[str, object]:
        return {
            "length": len(self.steps),
            "path": self.replay(),
            "reverse_path": self.reverse_trace(),
        }
