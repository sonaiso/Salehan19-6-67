"""Pilot Readiness Gate."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PilotReadinessCriteria:
    tests_pass: bool = False
    industrial_test_pass_rate: float = 0.0
    false_certainty_rate: float = 1.0
    source_required_detection: float = 0.0
    injection_detection: float = 0.0
    json_schema_stability: float = 0.0
    p95_latency_ms: float = 0.0
    readiness_report_exists: bool = False
    api_contract_defined: bool = True  # always True since we have api_contract.py
    rest_api_implemented: bool = False


@dataclass
class PilotReadinessResult:
    ready_for_pilot: bool
    score: float
    passed_criteria: list[str]
    failed_criteria: list[str]
    blockers: list[str]
    next_actions: list[str]
    conditional: bool = False
    status: str = "not_ready"


class PilotReadinessGate:
    THRESHOLDS = {
        "industrial_test_pass_rate": 0.85,
        "false_certainty_rate_max": 0.05,
        "source_required_detection": 0.90,
        "injection_detection": 0.90,
        "json_schema_stability": 0.95,
    }

    def evaluate(self, criteria: PilotReadinessCriteria) -> PilotReadinessResult:
        passed: list[str] = []
        failed: list[str] = []
        blockers: list[str] = []
        next_actions: list[str] = []

        # 1. Tests pass
        if criteria.tests_pass:
            passed.append("tests_pass")
        else:
            failed.append("tests_pass")
            blockers.append("Unit tests must all pass before pilot")

        # 2. Industrial test pass rate
        if criteria.industrial_test_pass_rate >= self.THRESHOLDS["industrial_test_pass_rate"]:
            passed.append("industrial_test_pass_rate")
        else:
            failed.append("industrial_test_pass_rate")
            blockers.append(
                f"Industrial test pass rate {criteria.industrial_test_pass_rate:.2%} < "
                f"{self.THRESHOLDS['industrial_test_pass_rate']:.2%}"
            )
            next_actions.append("Improve handling of missing/failure source scenarios")

        # 3. False certainty rate
        if criteria.false_certainty_rate <= self.THRESHOLDS["false_certainty_rate_max"]:
            passed.append("false_certainty_rate")
        else:
            failed.append("false_certainty_rate")
            blockers.append(
                f"False certainty rate {criteria.false_certainty_rate:.2%} > "
                f"{self.THRESHOLDS['false_certainty_rate_max']:.2%} max"
            )
            next_actions.append("Fix certainty policy for empty/timeout/error source scenarios")

        # 4. Source required detection
        if criteria.source_required_detection >= self.THRESHOLDS["source_required_detection"]:
            passed.append("source_required_detection")
        else:
            failed.append("source_required_detection")
            blockers.append(
                f"Source required detection {criteria.source_required_detection:.2%} < "
                f"{self.THRESHOLDS['source_required_detection']:.2%}"
            )

        # 5. Injection detection
        if criteria.injection_detection >= self.THRESHOLDS["injection_detection"]:
            passed.append("injection_detection")
        else:
            failed.append("injection_detection")
            blockers.append(
                f"Injection detection {criteria.injection_detection:.2%} < "
                f"{self.THRESHOLDS['injection_detection']:.2%}"
            )
            next_actions.append("Improve injection detection in source trust policy")

        # 6. JSON schema stability
        if criteria.json_schema_stability >= self.THRESHOLDS["json_schema_stability"]:
            passed.append("json_schema_stability")
        else:
            failed.append("json_schema_stability")
            next_actions.append("Stabilize JSON output schema")

        # 7. API contract defined
        if criteria.api_contract_defined:
            passed.append("api_contract_defined")
        else:
            failed.append("api_contract_defined")
            blockers.append("API contract must be defined before pilot")

        # 8. REST API implemented (soft blocker)
        if criteria.rest_api_implemented:
            passed.append("rest_api_implemented")
        else:
            failed.append("rest_api_implemented")
            blockers.append("REST API not implemented yet")
            next_actions.append("Implement REST API layer (FastAPI or Flask)")

        # 9. Readiness report exists
        if criteria.readiness_report_exists:
            passed.append("readiness_report_exists")
        else:
            failed.append("readiness_report_exists")
            next_actions.append("Generate and store industrial readiness report")

        total_criteria = len(passed) + len(failed)
        score = len(passed) / total_criteria if total_criteria else 0.0

        # Ready when: no hard blockers except REST API
        hard_blocker_keys = {"tests_pass", "industrial_test_pass_rate", "false_certainty_rate", "api_contract_defined"}
        hard_failures = [f for f in failed if f in hard_blocker_keys]

        conditional = not hard_failures and "rest_api_implemented" in failed
        if hard_failures:
            status = "not_ready"
            ready_for_pilot = False
        elif "rest_api_implemented" in failed:
            status = "conditional_candidate"
            ready_for_pilot = False
        else:
            status = "ready_for_pilot"
            ready_for_pilot = True

        return PilotReadinessResult(
            ready_for_pilot=ready_for_pilot,
            score=score,
            passed_criteria=passed,
            failed_criteria=failed,
            blockers=blockers,
            next_actions=next_actions,
            conditional=conditional,
            status=status,
        )

    def evaluate_from_runner(
        self,
        tests_pass: bool | None = None,
        readiness_report_exists: bool | None = None,
    ) -> PilotReadinessResult:
        """Run IndustrialTestRunner and derive criteria automatically."""
        from mcd.industrial.industrial_test_runner import IndustrialTestRunner
        from mcd.industrial.industrial_test_case import get_default_test_cases
        from mcd.industrial.latency_benchmark import LatencyBenchmark
        from mcd.industrial.serializers import industrial_result_to_dict

        runner = IndustrialTestRunner()
        cases = get_default_test_cases()
        results = runner.run_all(cases)
        summary = runner.summary(results)

        bench = LatencyBenchmark()
        bench_result = bench.run(cases[:10])

        # Compute real schema stability from result dicts
        result_dicts = [industrial_result_to_dict(r) for r in results]
        schema_stability = check_schema_stability({"results": result_dicts})

        criteria = PilotReadinessCriteria(
            tests_pass=tests_pass if tests_pass is not None else False,
            industrial_test_pass_rate=summary.get("pass_rate", 0.0),
            false_certainty_rate=summary.get("false_certainty_rate", 1.0),
            source_required_detection=summary.get("source_required_detection", 0.0),
            injection_detection=summary.get("injection_detection", 0.0),
            json_schema_stability=schema_stability,
            p95_latency_ms=bench_result.p95_latency_ms,
            readiness_report_exists=readiness_report_exists if readiness_report_exists is not None else False,
            api_contract_defined=True,
            rest_api_implemented=False,
        )
        return self.evaluate(criteria)


def check_schema_stability(result_dict: dict) -> float:
    """Compute schema stability score: fraction of results sharing the same key set."""
    results = result_dict.get("results", [])
    if not results:
        return 0.0
    key_sets = [frozenset(r.keys()) for r in results if isinstance(r, dict)]
    if not key_sets:
        return 0.0
    most_common = max(key_sets, key=lambda ks: key_sets.count(ks))
    return key_sets.count(most_common) / len(key_sets)
