"""Staging Simulator — simulates a controlled deployment environment."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.industrial.industrial_test_runner import IndustrialTestRunner, IndustrialResult
from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases


@dataclass
class StagingSimulationReport:
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    results: list[IndustrialResult]
    warnings: list[str] = field(default_factory=list)


class StagingSimulator:
    def __init__(self) -> None:
        self._runner = IndustrialTestRunner()

    def run(self, cases: list[IndustrialTestCase] | None = None) -> StagingSimulationReport:
        if cases is None:
            cases = get_default_test_cases()
        results = self._runner.run_all(cases)
        passed = sum(1 for r in results if r.passed)
        warnings: list[str] = []
        pass_rate = passed / len(results) if results else 0.0
        if pass_rate < 0.85:
            warnings.append(f"pass_rate_below_threshold: {pass_rate:.2%}")
        return StagingSimulationReport(
            total_cases=len(results),
            passed=passed,
            failed=len(results) - passed,
            pass_rate=pass_rate,
            results=results,
            warnings=warnings,
        )
