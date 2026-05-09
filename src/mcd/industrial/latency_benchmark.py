"""Latency Benchmark — measure pipeline component latencies."""
from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass, field

from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases


def percentile(values: list[float], p: float) -> float:
    """Compute p-th percentile using nearest-rank method."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    idx = max(0, min(math.ceil(p / 100.0 * n) - 1, n - 1))
    return sorted_v[idx]


@dataclass
class LatencyBenchmarkResult:
    total_cases: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    by_component: dict[str, float]
    warnings: list[str] = field(default_factory=list)


class LatencyBenchmark:
    def run(
        self,
        cases: list[IndustrialTestCase] | None = None,
        n: int = 20,
    ) -> LatencyBenchmarkResult:
        from mcd.industrial.industrial_test_runner import IndustrialTestRunner

        all_cases = get_default_test_cases()
        if cases is None:
            cases = all_cases[:n] if len(all_cases) >= n else all_cases

        runner = IndustrialTestRunner()
        latencies: list[float] = []
        for case in cases:
            t0 = time.monotonic()
            runner.run_case(case)
            latencies.append((time.monotonic() - t0) * 1000)

        if not latencies:
            return LatencyBenchmarkResult(
                total_cases=0,
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                max_latency_ms=0.0,
                by_component={"classification": 0.0, "source_retrieval": 0.0, "trust_evaluation": 0.0},
                warnings=["no_cases_to_benchmark"],
            )

        sorted_l = sorted(latencies)
        p50 = percentile(sorted_l, 50)
        p95 = percentile(sorted_l, 95)

        return LatencyBenchmarkResult(
            total_cases=len(latencies),
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            max_latency_ms=max(latencies),
            by_component={
                "classification": 0.0,
                "source_retrieval": 0.0,
                "trust_evaluation": 0.0,
            },
            warnings=["component_breakdown_not_yet_instrumented"],
        )
