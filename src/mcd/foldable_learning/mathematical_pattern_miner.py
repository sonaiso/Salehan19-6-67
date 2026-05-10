"""MathematicalPatternMiner — mines patterns from lists of CognitiveResiduals."""
from __future__ import annotations
from dataclasses import dataclass
from mcd.residual_learning.residual_schema import CognitiveResidual

__all__ = ["MathematicalPatternMiner", "MinedPattern"]


@dataclass
class MinedPattern:
    pattern_id: str
    frequency: int
    graph_motif: str
    vector_signature: dict
    residual_type: str
    proposed_invariant: str
    proposed_test: str

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "frequency": self.frequency,
            "graph_motif": self.graph_motif,
            "vector_signature": self.vector_signature,
            "residual_type": self.residual_type,
            "proposed_invariant": self.proposed_invariant,
            "proposed_test": self.proposed_test,
        }


class MathematicalPatternMiner:
    _THRESHOLD = 3

    def mine(self, residuals: list[CognitiveResidual]) -> list[MinedPattern]:
        if not residuals:
            return []
        total = len(residuals)
        type_groups: dict[str, list[CognitiveResidual]] = {}
        for r in residuals:
            for rt in r.residual_types:
                type_groups.setdefault(rt, []).append(r)

        patterns = []
        for rtype, group in type_groups.items():
            if len(group) >= self._THRESHOLD:
                patterns.append(MinedPattern(
                    pattern_id=f"PATTERN-{rtype.upper().replace('_', '-')}-{len(group):03d}",
                    frequency=len(group),
                    graph_motif=rtype.replace("_residual", ""),
                    vector_signature={rtype: round(len(group) / total, 4)},
                    residual_type=rtype,
                    proposed_invariant=f"invariant: no {rtype} in verified proposals",
                    proposed_test=f"test_no_{rtype}_in_verified_proposal",
                ))
        return patterns

    def get_proposed_invariants(self, residuals: list[CognitiveResidual]) -> list[str]:
        return [p.proposed_invariant for p in self.mine(residuals)]
