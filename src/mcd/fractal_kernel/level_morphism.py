from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class LevelMorphism:
    morphism_id: str
    source_level: str
    target_level: str
    preserves: list[str] = field(default_factory=list)  # trace, relation, vector, evidence, certainty, proof
    allowed_loss: list[str] = field(default_factory=list)
    required_metadata: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "morphism_id": self.morphism_id,
            "source_level": self.source_level,
            "target_level": self.target_level,
            "preserves": self.preserves,
            "allowed_loss": self.allowed_loss,
            "required_metadata": self.required_metadata,
        }


# Built-in registry of level morphisms
_DEFAULT_MORPHISMS: list[LevelMorphism] = [
    LevelMorphism("M-unicode-grapheme", "unicode", "grapheme",
                  preserves=["trace", "relation"], allowed_loss=["vector"]),
    LevelMorphism("M-grapheme-token", "grapheme", "token",
                  preserves=["trace", "relation", "vector"], allowed_loss=[]),
    LevelMorphism("M-token-word", "token", "word",
                  preserves=["trace", "relation", "vector", "evidence"], allowed_loss=[]),
    LevelMorphism("M-word-folded_word_graph", "word", "fold_pattern",
                  preserves=["trace", "relation", "vector", "evidence", "certainty"], allowed_loss=["surface_details"]),
    LevelMorphism("M-fold_pattern-concept", "fold_pattern", "concept",
                  preserves=["trace", "relation", "vector", "evidence", "certainty", "proof"], allowed_loss=[]),
    LevelMorphism("M-mabni-judgment", "mabni", "judgment",
                  preserves=["trace", "relation", "vector"], allowed_loss=["certainty"]),
    LevelMorphism("M-murab-relational", "murab", "sentence",
                  preserves=["trace", "relation"], allowed_loss=["vector"]),
    LevelMorphism("M-sentence-cognitive_graph", "sentence", "concept",
                  preserves=["trace", "relation", "vector", "evidence"], allowed_loss=[]),
    LevelMorphism("M-concept-proof", "concept", "proof",
                  preserves=["trace", "relation", "vector", "evidence", "certainty", "proof"], allowed_loss=[]),
    LevelMorphism("M-residual-fold_pattern", "residual", "fold_pattern",
                  preserves=["trace", "relation"], allowed_loss=["vector", "evidence"]),
]


class LevelMorphismRegistry:
    def __init__(self) -> None:
        self._morphisms: dict[str, LevelMorphism] = {m.morphism_id: m for m in _DEFAULT_MORPHISMS}

    def register(self, morphism: LevelMorphism) -> None:
        self._morphisms[morphism.morphism_id] = morphism

    def get(self, morphism_id: str) -> Optional[LevelMorphism]:
        return self._morphisms.get(morphism_id)

    def find(self, source_level: str, target_level: str) -> Optional[LevelMorphism]:
        for m in self._morphisms.values():
            if m.source_level == source_level and m.target_level == target_level:
                return m
        return None

    def get_all(self) -> list[LevelMorphism]:
        return list(self._morphisms.values())

    def validate_transition(self, source_level: str, target_level: str) -> tuple[bool, list[str]]:
        """Returns (valid, warnings)."""
        morphism = self.find(source_level, target_level)
        if morphism is None:
            return False, [f"No morphism registered for {source_level} → {target_level}"]
        warnings = []
        if "evidence" not in morphism.preserves and "evidence" not in morphism.allowed_loss:
            warnings.append(f"Morphism {morphism.morphism_id} does not declare evidence handling")
        if "trace" not in morphism.preserves and "trace" not in morphism.allowed_loss:
            warnings.append(f"Morphism {morphism.morphism_id} does not declare trace handling")
        return True, warnings
