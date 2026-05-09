"""Data models for Fractal Prompt Classification Layer (FPCL)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClassificationScore:
    """A labelled numeric score with an optional explanation."""

    label: str
    score: float
    reason: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"score must be in [0, 1], got {self.score}")
        if not self.label:
            raise ValueError("label must not be empty")


@dataclass(frozen=True)
class PromptConcept:
    """A single concept extracted from a prompt."""

    surface: str
    normalized: str
    span_start: int | None = None
    span_end: int | None = None
    root_domain: dict[str, float] = field(default_factory=dict)
    concept_type: dict[str, float] = field(default_factory=dict)
    knowledge_category: dict[str, float] = field(default_factory=dict)
    judgment_hint: dict[str, float] = field(default_factory=dict)
    evidence_hint: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface,
            "normalized": self.normalized,
            "span_start": self.span_start,
            "span_end": self.span_end,
            "root_domain": dict(self.root_domain),
            "concept_type": dict(self.concept_type),
            "knowledge_category": dict(self.knowledge_category),
            "judgment_hint": dict(self.judgment_hint),
            "evidence_hint": dict(self.evidence_hint),
        }


@dataclass
class PromptFrame:
    """Full classification frame for a prompt."""

    raw_text: str
    normalized_text: str
    intent: str
    concepts: list[PromptConcept]

    root_domain: dict[str, float]
    concept_types: dict[str, float]
    knowledge_categories: dict[str, float]
    judgment_types: dict[str, float]
    evidence_needs: dict[str, float]

    certainty_policy: str
    certainty_reason: str

    routing_engine: str
    sub_engines: list[str]

    warnings: list[str] = field(default_factory=list)
    debug: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "intent": self.intent,
            "concepts": [c.to_dict() for c in self.concepts],
            "root_domain": dict(self.root_domain),
            "concept_types": dict(self.concept_types),
            "knowledge_categories": dict(self.knowledge_categories),
            "judgment_types": dict(self.judgment_types),
            "evidence_needs": dict(self.evidence_needs),
            "certainty_policy": self.certainty_policy,
            "certainty_reason": self.certainty_reason,
            "routing_engine": self.routing_engine,
            "sub_engines": list(self.sub_engines),
            "warnings": list(self.warnings),
            "debug": dict(self.debug),
        }
