"""PatternMemory — in-memory store for FoldSignatures."""
from __future__ import annotations
from .fold_schema import FoldSignature
from mcd.residual_learning.residual_schema import CognitiveResidual

__all__ = ["PatternMemory"]


class PatternMemory:
    def __init__(self) -> None:
        self._folds: list[FoldSignature] = []

    def add_fold_signature(self, sig: FoldSignature) -> None:
        self._folds.append(sig)

    def search_by_residual_type(self, rtype: str) -> list[FoldSignature]:
        return [f for f in self._folds if rtype in f.residual_types]

    def search_by_domain(self, domain: str) -> list[FoldSignature]:
        return [f for f in self._folds if domain in f.domain_signature]

    def search_by_graph_shape(self, shape: str) -> list[FoldSignature]:
        return [f for f in self._folds if shape.lower() in f.graph_shape.lower()]

    def search_by_vector_similarity(self, vector: dict) -> list[FoldSignature]:
        results = []
        for f in self._folds:
            if any(k in f.vector_signature for k in vector):
                results.append(f)
        return results

    def recall_similar_case(self, residual: CognitiveResidual) -> list[FoldSignature]:
        results = []
        for rt in residual.residual_types:
            for f in self.search_by_residual_type(rt):
                if f not in results:
                    results.append(f)
        return results

    def export_memory(self) -> list[dict]:
        return [f.to_dict() for f in self._folds]

    def size(self) -> int:
        return len(self._folds)
