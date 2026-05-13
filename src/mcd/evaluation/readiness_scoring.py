"""Readiness scoring from empirical benchmark outputs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from mcd.evaluation.benchmark_runner import REQUIRED_BENCHMARK_METRICS


@dataclass
class ReadinessReport:
    generated_at: str
    governance_readiness: float
    industrial_readiness: float
    scientific_readiness: float
    operational_readiness: float
    audit_readiness: float
    production_ready: bool
    production_readiness_rule: str
    final_judgment_contract: list[str]
    benchmark_metrics: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "governance_readiness": self.governance_readiness,
            "industrial_readiness": self.industrial_readiness,
            "scientific_readiness": self.scientific_readiness,
            "operational_readiness": self.operational_readiness,
            "audit_readiness": self.audit_readiness,
            "production_ready": self.production_ready,
            "production_readiness_rule": self.production_readiness_rule,
            "final_judgment_contract": list(self.final_judgment_contract),
            "benchmark_metrics": dict(self.benchmark_metrics),
        }


def _metric(metrics: dict[str, float], key: str) -> float:
    return round(float(metrics.get(key, 0.0)), 4)


def build_readiness_report(metrics: dict[str, float]) -> ReadinessReport:
    governance = round(
        (
            _metric(metrics, "illicit_certification_block_rate")
            + _metric(metrics, "forbidden_transition_detection_rate")
            + _metric(metrics, "adversarial_downgrade_accuracy")
        )
        / 3
        * 5,
        2,
    )
    industrial = round(
        (
            _metric(metrics, "residual_preservation_rate")
            + _metric(metrics, "trace_completeness_score")
        )
        / 2
        * 5,
        2,
    )
    scientific = round(
        (
            _metric(metrics, "replay_success_rate")
            + _metric(metrics, "distributed_consistency_rate")
        )
        / 2
        * 5,
        2,
    )
    audit = round(
        (
            _metric(metrics, "trace_completeness_score")
            + _metric(metrics, "replay_success_rate")
            + _metric(metrics, "residual_preservation_rate")
        )
        / 3
        * 5,
        2,
    )
    operational = round((governance + industrial + scientific + audit) / 4, 2)
    production_ready = (
        governance >= 4.5
        and industrial >= 4.5
        and scientific >= 4.5
        and operational >= 4.5
        and audit >= 4.5
    )

    required_metrics = {name: _metric(metrics, name) for name in REQUIRED_BENCHMARK_METRICS}
    return ReadinessReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        governance_readiness=governance,
        industrial_readiness=industrial,
        scientific_readiness=scientific,
        operational_readiness=operational,
        audit_readiness=audit,
        production_ready=production_ready,
        production_readiness_rule=(
            "all readiness dimensions must be >= 4.5 and derive from empirical benchmark metrics"
        ),
        final_judgment_contract=["ZERO", "HYPOTHESIS", "CERTIFICATE"],
        benchmark_metrics=required_metrics,
    )


def readiness_report_markdown(report: ReadinessReport) -> str:
    lines = [
        "# Readiness Report",
        "",
        f"- Governance readiness: {report.governance_readiness}/5",
        f"- Industrial readiness: {report.industrial_readiness}/5",
        f"- Scientific readiness: {report.scientific_readiness}/5",
        f"- Operational readiness: {report.operational_readiness}/5",
        f"- Audit readiness: {report.audit_readiness}/5",
        f"- Production ready: {report.production_ready}",
        "",
        "## Empirical Benchmark Metrics",
        "",
    ]
    for metric_name in REQUIRED_BENCHMARK_METRICS:
        lines.append(f"- {metric_name}: {report.benchmark_metrics.get(metric_name, 0.0):.4f}")
    return "\n".join(lines) + "\n"


def readiness_report_json(report: ReadinessReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
