"""IndustrialBridge — converts curriculum Level 7/8 units to IndustrialTestCase."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .cognitive_unit import CognitiveUnit


@dataclass
class CurriculumIndustrialCase:
    """An industrial test case derived from a curriculum unit."""
    case_id: str
    input_text: str
    source_unit_id: str
    expected_behavior: str
    expected_minimum_warnings: list[str] = field(default_factory=list)
    forbidden_behaviors: list[str] = field(default_factory=list)
    expected_certainty_policy: str = "insufficient_evidence"
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "input_text": self.input_text,
            "source_unit_id": self.source_unit_id,
            "expected_behavior": self.expected_behavior,
            "expected_minimum_warnings": self.expected_minimum_warnings,
            "forbidden_behaviors": self.forbidden_behaviors,
            "expected_certainty_policy": self.expected_certainty_policy,
            "difficulty": self.difficulty,
            "tags": self.tags,
        }


_BEHAVIOR_MAP = {
    "insufficient_evidence": "suspend",
    "suspend_judgment": "suspend",
    "probable_knowledge": "answer_with_evidence",
    "possible_knowledge": "lower_certainty",
    "certain_knowledge": "answer_with_evidence",
    "near_certainty": "answer_with_evidence",
}

_FORBIDDEN_BEHAVIOR_MAP: dict[str, list[str]] = {
    "fabricated_statistic": ["fabricated_statistic"],
    "false_certainty": ["false_certainty"],
    "harm_equals_haram": ["harm_equals_haram"],
    "follow_injection": ["follow_injection"],
    "ignore_conflict": ["ignore_conflict"],
    "present_stale_as_current": ["present_stale_as_current"],
    "accept_ambiguous_without_context": ["accept_ambiguous_without_context"],
}


class IndustrialBridge:
    """Converts Level 7 and Level 8 curriculum units to industrial test cases."""

    def convert(self, units: list[CognitiveUnit]) -> list[CurriculumIndustrialCase]:
        """Convert Level 7/8 units to industrial test cases."""
        cases = []
        eligible = [u for u in units if u.level in (7, 8)]
        for i, unit in enumerate(eligible, start=1):
            case_id = f"CURR-IND-{i:04d}"
            behavior = _BEHAVIOR_MAP.get(unit.certainty_policy, "suspend")

            forbidden: list[str] = []
            for w in unit.expected_warnings + unit.forbidden_confusions:
                if w in _FORBIDDEN_BEHAVIOR_MAP:
                    forbidden.extend(_FORBIDDEN_BEHAVIOR_MAP[w])
            forbidden = list(dict.fromkeys(forbidden))

            cases.append(CurriculumIndustrialCase(
                case_id=case_id,
                input_text=unit.input_text,
                source_unit_id=unit.unit_id,
                expected_behavior=behavior,
                expected_minimum_warnings=list(unit.expected_warnings),
                forbidden_behaviors=forbidden,
                expected_certainty_policy=unit.certainty_policy,
                difficulty=unit.difficulty,
                tags=list(unit.tags),
            ))
        return cases

    def export_to_jsonl(self, cases: list[CurriculumIndustrialCase]) -> str:
        """Export cases as JSONL string."""
        return "\n".join(json.dumps(c.to_dict(), ensure_ascii=False) for c in cases)
