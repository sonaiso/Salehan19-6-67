"""Industrial testing package — Phase 5."""
from __future__ import annotations

from mcd.industrial.api_contract import (
    SourceQuery,
    SourceDocument,
    SourceAPIResponse,
)
from mcd.industrial.source_api_adapter import BaseSourceAPIAdapter, NullSourceAPIAdapter
from mcd.industrial.mock_source_api import MockSourceAPI
from mcd.industrial.source_trust_policy import SourceTrustPolicy, SourceTrustResult
from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases
from mcd.industrial.industrial_test_runner import IndustrialTestRunner, IndustrialResult
from mcd.industrial.staging_simulator import StagingSimulator, StagingSimulationReport
from mcd.industrial.latency_benchmark import LatencyBenchmark, LatencyBenchmarkResult
from mcd.industrial.failure_injection import FailureInjector, FailureInjectionResult
from mcd.industrial.api_observability import ObservabilityTracer, RequestTrace, StageTrace
from mcd.industrial.pilot_readiness import PilotReadinessGate, PilotReadinessResult, PilotReadinessCriteria

__all__ = [
    "SourceQuery",
    "SourceDocument",
    "SourceAPIResponse",
    "BaseSourceAPIAdapter",
    "NullSourceAPIAdapter",
    "MockSourceAPI",
    "SourceTrustPolicy",
    "SourceTrustResult",
    "IndustrialTestCase",
    "get_default_test_cases",
    "IndustrialTestRunner",
    "IndustrialResult",
    "StagingSimulator",
    "StagingSimulationReport",
    "LatencyBenchmark",
    "LatencyBenchmarkResult",
    "FailureInjector",
    "FailureInjectionResult",
    "ObservabilityTracer",
    "RequestTrace",
    "StageTrace",
    "PilotReadinessGate",
    "PilotReadinessResult",
    "PilotReadinessCriteria",
]
