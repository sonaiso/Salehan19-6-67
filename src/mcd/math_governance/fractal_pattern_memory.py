from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FractalPattern:
    pattern_id: str
    pattern_type: str
    graph_shape: str = ""
    operator_chain: list[str] = field(default_factory=list)
    evidence_signature: str = "missing"
    certainty_signature: str = "suspend"
    residual_signature: str = "none"
    recall_keys: list[str] = field(default_factory=list)
    recommended_action: str = "review"

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "graph_shape": self.graph_shape,
            "operator_chain": self.operator_chain,
            "evidence_signature": self.evidence_signature,
            "certainty_signature": self.certainty_signature,
            "residual_signature": self.residual_signature,
            "recall_keys": self.recall_keys,
            "recommended_action": self.recommended_action,
        }


class FractalPatternMemory:
    def __init__(self) -> None:
        self._patterns: dict[str, FractalPattern] = {}

    def add_pattern(self, pattern: FractalPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def recall_by_text_features(self, features: list[str]) -> list[FractalPattern]:
        feature_set = set(features)
        return [p for p in self._patterns.values() if feature_set.intersection(set(p.recall_keys))]

    def recall_by_residual(self, residual: str) -> list[FractalPattern]:
        return [p for p in self._patterns.values() if p.residual_signature == residual]

    def recall_by_operator_chain(self, chain: list[str]) -> list[FractalPattern]:
        return [p for p in self._patterns.values() if p.operator_chain == chain]

    def export(self) -> list[dict]:
        return [p.to_dict() for p in self._patterns.values()]
