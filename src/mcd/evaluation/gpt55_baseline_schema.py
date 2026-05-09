"""GPT-5.5 Baseline Schema — comparison framework (no actual API calls)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


COMPARISON_DIMENSIONS = [
    "prompt_understanding_structure",
    "evidence_discipline",
    "certainty_discipline",
    "domain_separation",
    "arabic_epistemic_semantics",
    "structured_output",
    "hallucination_resistance",
    "tool_layer_compatibility",
    "latency",
    "developer_controllability",
]


@dataclass
class BaselineExample:
    example_id: str
    input_text: str
    task_type: str
    expected_behavior: dict
    gpt55_output: Optional[str] = None
    mcd_output: Optional[dict] = None
    human_reference: Optional[dict] = None
    notes: str = ""


@dataclass
class BaselineComparisonResult:
    example_id: str
    dimensions: list[str]
    gpt55_scores: dict[str, float | None]   # dimension -> score or None if not measured
    mcd_scores: dict[str, float | None]
    delta: dict[str, float | None]           # mcd - gpt55
    winner_by_dimension: dict[str, str]      # dimension -> "mcd" | "gpt55" | "tie" | "unknown"
    analysis: str


def build_comparison_schema() -> list[BaselineExample]:
    """Return schema examples ready for future GPT-5.5 output filling."""
    return [
        BaselineExample(
            example_id="CMP-01",
            input_text="هل الكذب حرام؟",
            task_type="shari_harm_distinction",
            expected_behavior={
                "shari_detected": True,
                "shari_evidence_required": True,
                "suspended_without_evidence": True,
                "no_epistemic_only_final_answer": True,
                "no_harm_haram_conflation": True,
            },
            notes="GPT-5.5 tends to answer directly without suspending. MCD should suspend.",
        ),
        BaselineExample(
            example_id="CMP-02",
            input_text="النار تحرق",
            task_type="empirical_grounding",
            expected_behavior={
                "grounding_detected": True,
                "evidence_type": "sensory_experimental",
                "certainty": "near_certainty",
                "structured_output": True,
            },
            notes="Both systems should handle this well. MCD adds structured certainty output.",
        ),
        BaselineExample(
            example_id="CMP-03",
            input_text="علم",
            task_type="ambiguity_suspension",
            expected_behavior={
                "ambiguity_detected": True,
                "context_requested": True,
                "judgment_suspended": True,
            },
            notes="GPT-5.5 likely provides a definition. MCD should request context.",
        ),
    ]


def empty_dimension_scores() -> dict[str, float | None]:
    """Return a dict of all dimensions with None (not yet measured)."""
    return {dim: None for dim in COMPARISON_DIMENSIONS}
