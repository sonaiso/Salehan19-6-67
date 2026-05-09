"""Industrial Test Case definition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

EvaluatorRole = Literal[
    "ai_evaluator",
    "rag_engineer",
    "prompt_engineer",
    "safety_reviewer",
    "product_manager",
    "education_evaluator",
    "enterprise_reviewer",
]
SourceAPIScenario = Literal[
    "ok_with_relevant_docs",
    "ok_with_irrelevant_docs",
    "empty",
    "timeout",
    "error",
    "conflicting_docs",
    "stale_docs",
    "low_authority_docs",
    "injection_contaminated_doc",
    "missing_source",
]
ExpectedBehavior = Literal[
    "answer_with_evidence",
    "suspend",
    "request_source",
    "detect_injection",
    "lower_certainty",
    "flag_conflict",
    "output_structured_json",
]


@dataclass
class IndustrialTestCase:
    case_id: str
    input_text: str
    evaluator_role: EvaluatorRole = "ai_evaluator"
    source_api_scenario: SourceAPIScenario = "ok_with_relevant_docs"
    expected_behavior: ExpectedBehavior = "answer_with_evidence"
    expected_minimum_warnings: list[str] = field(default_factory=list)
    forbidden_behaviors: list[str] = field(default_factory=list)
    expected_certainty_policy: str = ""
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)


import json as _json
from pathlib import Path as _Path

_JSONL_PATH = _Path(__file__).parent.parent.parent.parent / "data" / "industrial" / "industrial_test_cases_ar.jsonl"


def get_default_test_cases() -> list[IndustrialTestCase]:
    """Load industrial test cases from JSONL (single source of truth)."""
    if _JSONL_PATH.exists():
        cases = []
        with open(_JSONL_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = _json.loads(line)
                cases.append(IndustrialTestCase(
                    case_id=data["case_id"],
                    input_text=data["input_text"],
                    evaluator_role=data.get("evaluator_role", "ai_evaluator"),
                    source_api_scenario=data.get("source_api_scenario", "ok_with_relevant_docs"),
                    expected_behavior=data.get("expected_behavior", "answer_with_evidence"),
                    expected_minimum_warnings=data.get("expected_minimum_warnings", []),
                    forbidden_behaviors=data.get("forbidden_behaviors", []),
                    expected_certainty_policy=data.get("expected_certainty_policy", ""),
                    difficulty=data.get("difficulty", "medium"),
                    tags=data.get("tags", []),
                ))
        if cases:
            return cases
    import warnings as _warnings
    _warnings.warn("industrial_test_cases_ar.jsonl not found, using minimal smoke cases", RuntimeWarning)
    return _minimal_smoke_cases()


def _minimal_smoke_cases() -> list[IndustrialTestCase]:
    return [
        IndustrialTestCase(
            case_id="SMOKE-001",
            input_text="اختبار أساسي",
            source_api_scenario="empty",
            expected_behavior="suspend",
            expected_minimum_warnings=["source_required"],
            expected_certainty_policy="insufficient_evidence",
        )
    ]
