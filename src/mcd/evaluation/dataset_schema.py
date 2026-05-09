"""Dataset schema — BenchmarkExample dataclass for Phase 4 evaluation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


SourceType = Literal["static_gold", "dynamic_generated", "adversarial", "ambiguity", "calibration", "regression"]
CertaintyPolicyType = Literal["near_certainty", "strong_knowledge", "probable_knowledge", "hypothesis", "suspend"]
EpistemicStatusType = Literal["verified", "probable", "hypothesis", "suspended", "rejected", "requires_context"]
DifficultyType = Literal["easy", "medium", "hard", "adversarial"]


@dataclass
class BenchmarkExample:
    example_id: str
    input_text: str
    language: str = "ar"
    source_type: SourceType = "static_gold"
    expected_root_domains: dict[str, float] = field(default_factory=dict)
    expected_concept_types: dict[str, float] = field(default_factory=dict)
    expected_knowledge_categories: dict[str, float] = field(default_factory=dict)
    expected_judgment_types: dict[str, float] = field(default_factory=dict)
    expected_evidence_needs: dict[str, float] = field(default_factory=dict)
    expected_certainty_policy: CertaintyPolicyType = "suspend"
    expected_epistemic_status: EpistemicStatusType = "suspended"
    required_warnings: list[str] = field(default_factory=list)
    forbidden_outputs: list[str] = field(default_factory=list)
    required_separations: list[str] = field(default_factory=list)
    notes: str = ""
    difficulty: DifficultyType = "medium"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "example_id": self.example_id,
            "input_text": self.input_text,
            "language": self.language,
            "source_type": self.source_type,
            "expected_root_domains": self.expected_root_domains,
            "expected_concept_types": self.expected_concept_types,
            "expected_knowledge_categories": self.expected_knowledge_categories,
            "expected_judgment_types": self.expected_judgment_types,
            "expected_evidence_needs": self.expected_evidence_needs,
            "expected_certainty_policy": self.expected_certainty_policy,
            "expected_epistemic_status": self.expected_epistemic_status,
            "required_warnings": self.required_warnings,
            "forbidden_outputs": self.forbidden_outputs,
            "required_separations": self.required_separations,
            "notes": self.notes,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BenchmarkExample":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
