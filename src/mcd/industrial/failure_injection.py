"""Failure Injection — test robustness under failure conditions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mcd.industrial.mock_source_api import MockSourceAPI, MockScenario
from mcd.industrial.api_contract import SourceQuery
from mcd.industrial.industrial_test_case import IndustrialTestCase

FailureScenario = Literal[
    "source_timeout",
    "source_empty",
    "source_conflict",
    "source_stale",
    "invalid_json_response",
    "slow_response",
    "low_authority_source",
    "prompt_injection_in_source",
    "missing_evidence",
    "contradictory_claims",
]

SCENARIO_TO_MOCK: dict[str, str] = {
    "source_timeout": "timeout",
    "source_empty": "empty",
    "source_conflict": "conflicting_docs",
    "source_stale": "stale_docs",
    "invalid_json_response": "error",
    "slow_response": "timeout",
    "low_authority_source": "low_authority_docs",
    "prompt_injection_in_source": "injection_contaminated_doc",
    "missing_evidence": "missing_source",
    "contradictory_claims": "conflicting_docs",
}


@dataclass
class FailureInjectionResult:
    scenario: str
    passed: bool
    certainty_lowered: bool
    suspended: bool
    has_warnings: bool
    no_fabricated_answer: bool
    details: str


class FailureInjector:
    def run_scenario(
        self, scenario: FailureScenario, input_text: str = "اختبار النظام"
    ) -> FailureInjectionResult:
        from mcd.industrial.industrial_test_runner import IndustrialTestRunner
        from mcd.industrial.industrial_test_case import IndustrialTestCase

        mock_scenario = SCENARIO_TO_MOCK.get(scenario, "empty")
        case = IndustrialTestCase(
            case_id=f"FI-{scenario}",
            input_text=input_text,
            source_api_scenario=mock_scenario,  # type: ignore[arg-type]
            expected_behavior="suspend",
        )
        runner = IndustrialTestRunner()
        result = runner.run_case(case)

        certainty_lowered = result.certainty_policy != "certain"
        suspended = result.certainty_policy in ("suspend", "insufficient_evidence")
        has_warnings = len(result.warnings) > 0
        no_fabricated_answer = result.certainty_policy != "certain"

        passed = certainty_lowered and has_warnings

        return FailureInjectionResult(
            scenario=scenario,
            passed=passed,
            certainty_lowered=certainty_lowered,
            suspended=suspended,
            has_warnings=has_warnings,
            no_fabricated_answer=no_fabricated_answer,
            details=result.explanation,
        )

    def run_all(self) -> list[FailureInjectionResult]:
        scenarios: list[FailureScenario] = list(SCENARIO_TO_MOCK.keys())  # type: ignore[assignment]
        return [self.run_scenario(s) for s in scenarios]
