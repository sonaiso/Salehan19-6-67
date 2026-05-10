"""AdversarialCurriculum — loads and analyzes adversarial examples."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "curriculum"

ADVERSARIAL_CATEGORIES: list[str] = [
    "input_label_trap",
    "ambiguous_words",
    "harm_haram_conflation",
    "api_as_evidence_trap",
    "tool_as_authority_trap",
    "metaphor_literalization",
    "analogy_without_illah",
    "fake_evidence",
    "popularity_as_evidence",
    "stale_source",
    "prompt_injection",
    "high_stakes",
    "conflicting_sources",
    "over_certainty",
    # Phase 7.1 — extended adversarial categories
    "false_certainty",
    "false_generalization",
    "injection_attempt",
    "tool_authority_claim",
    "metaphor_as_literal",
    "ad_hominem",
    "anchoring_bias",
    "appeal_to_authority",
    "appeal_to_popularity",
    "availability_heuristic",
    "cherry_picking",
    "circular_reasoning",
    "confirmation_bias",
    "correlation_causation",
    "domain_conflation",
    "false_dilemma",
    "false_equivalence",
    "hasty_generalization",
    "label_only",
    "missing_evidence",
    "post_hoc_fallacy",
    "red_herring",
    "single_source",
    "slippery_slope",
    "strawman",
    "sunk_cost_fallacy",
    "survivorship_bias",
    "vector_collapse",
]


@dataclass
class AdversarialExample:
    example_id: str
    input_text: str
    adversarial_category: str
    expected_detection: str
    forbidden_confusions: list[str] = field(default_factory=list)
    expected_certainty_policy: str = "suspend_judgment"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "example_id": self.example_id,
            "input_text": self.input_text,
            "adversarial_category": self.adversarial_category,
            "expected_detection": self.expected_detection,
            "forbidden_confusions": self.forbidden_confusions,
            "expected_certainty_policy": self.expected_certainty_policy,
            "tags": self.tags,
        }


def load_adversarial_examples() -> list[AdversarialExample]:
    path = _DATA_DIR / "adversarial_curriculum_ar.jsonl"
    if not path.exists():
        return []
    examples = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        examples.append(AdversarialExample(
            example_id=d["example_id"],
            input_text=d["input_text"],
            adversarial_category=d.get("adversarial_category", "unknown"),
            expected_detection=d.get("expected_detection", ""),
            forbidden_confusions=d.get("forbidden_confusions", []),
            expected_certainty_policy=d.get("expected_certainty_policy", "suspend_judgment"),
            tags=d.get("tags", []),
        ))
    return examples
