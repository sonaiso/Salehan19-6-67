"""Prometheus-compatible governance metrics exporter."""
from __future__ import annotations

from typing import Any

from mcd.observability.runtime_metrics import collect_runtime_metrics


def _line_help(metric: str, description: str) -> str:
    return f"# HELP {metric} {description}"


def _line_type(metric: str, metric_type: str = "gauge") -> str:
    return f"# TYPE {metric} {metric_type}"


def export_prometheus_metrics() -> str:
    snapshot = collect_runtime_metrics()
    profile = snapshot.profile or "unknown"
    lines: list[str] = []

    lines.extend(
        [
            _line_help("mcd_trace_event_count", "Total durable trace events"),
            _line_type("mcd_trace_event_count"),
            f"mcd_trace_event_count {snapshot.trace_event_count}",
            _line_help("mcd_governance_event_count", "Total immutable governance log events"),
            _line_type("mcd_governance_event_count"),
            f"mcd_governance_event_count {snapshot.governance_event_count}",
            _line_help("mcd_replay_success", "Replay integrity status (1=success, 0=failed)"),
            _line_type("mcd_replay_success"),
            f"mcd_replay_success {1 if snapshot.replay_success else 0}",
            _line_help("mcd_event_log_immutable", "Immutable event log status (1=valid, 0=invalid)"),
            _line_type("mcd_event_log_immutable"),
            f"mcd_event_log_immutable {1 if snapshot.immutable_event_log_valid else 0}",
        ]
    )

    for name, value in snapshot.governance_metrics.items():
        metric = f"mcd_{name}"
        lines.append(_line_help(metric, f"Governance metric: {name}"))
        lines.append(_line_type(metric))
        lines.append(f'{metric}{{profile="{profile}"}} {value}')

    return "\n".join(lines) + "\n"


def export_metrics_json() -> dict[str, Any]:
    return collect_runtime_metrics().to_dict()
