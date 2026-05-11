from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

PATTERN_TYPES = {
    "residual", "evidence_gap", "certainty_cap", "operator_conflict",
    "morphosemantic_shape", "mabni_shape", "murab_shape", "proof_shape"
}


@dataclass
class FractalPattern:
    pattern_id: str
    pattern_type: str
    graph_shape: dict = field(default_factory=dict)
    vector_signature: dict[str, float] = field(default_factory=dict)
    recall_keys: list[str] = field(default_factory=list)
    unfold_plan: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.pattern_type not in PATTERN_TYPES:
            raise ValueError(f"Invalid pattern_type: {self.pattern_type}")

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "graph_shape": self.graph_shape,
            "vector_signature": self.vector_signature,
            "recall_keys": self.recall_keys,
            "unfold_plan": self.unfold_plan,
            "examples": self.examples,
            "counterexamples": self.counterexamples,
            "invariants": self.invariants,
        }


class PatternMemory:
    def __init__(self) -> None:
        self._patterns: dict[str, FractalPattern] = {}

    def add_pattern(self, pattern: FractalPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def search_by_type(self, pattern_type: str) -> list[FractalPattern]:
        return [p for p in self._patterns.values() if p.pattern_type == pattern_type]

    def search_by_graph_shape(self, shape_key: str) -> list[FractalPattern]:
        return [p for p in self._patterns.values() if shape_key in str(p.graph_shape)]

    def search_by_vector_signature(self, sig: dict[str, float], tolerance: float = 0.1) -> list[FractalPattern]:
        results = []
        for p in self._patterns.values():
            match = all(
                abs(p.vector_signature.get(k, 0.0) - v) <= tolerance
                for k, v in sig.items()
            )
            if match:
                results.append(p)
        return results

    def recall(self, recall_key: str) -> list[FractalPattern]:
        return [p for p in self._patterns.values() if recall_key in p.recall_keys]

    def export(self) -> list[dict]:
        return [p.to_dict() for p in self._patterns.values()]

    def __len__(self) -> int:
        return len(self._patterns)
