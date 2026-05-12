"""Empirical governance benchmark runner for PR #71."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from mcd.audit.replay import replay_trace_events
from mcd.governance.adversarial_validation import (
    FORBIDDEN_TRANSITIONS,
    AdversarialAttempt,
)
from mcd.governance.distributed_simulation import (
    DistributedAgentAttempt,
    run_distributed_governance_simulation,
)
from mcd.metrics import compute_governance_metrics


REQUIRED_BENCHMARK_METRICS: tuple[str, ...] = (
    "illicit_certification_block_rate",
    "forbidden_transition_detection_rate",
    "residual_preservation_rate",
    "replay_success_rate",
    "distributed_consistency_rate",
    "trace_completeness_score",
    "adversarial_downgrade_accuracy",
)


@dataclass(frozen=True)
class GovernanceBenchmarkCase:
    case_id: str
    agent_id: str
    attempt: AdversarialAttempt
    expected_downgrade: bool
    expected_illicit_block: bool
    expected_forbidden_detection: bool
    requires_residual_preservation: bool
    trace_complete: bool = True
    replay_event_valid: bool = True


@dataclass
class BenchmarkRunReport:
    generated_at: str
    total_cases: int
    metrics: dict[str, float]
    metric_counts: dict[str, dict[str, int]]
    consistency_violations: list[str]
    cases: list[dict]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "total_cases": self.total_cases,
            "metrics": dict(self.metrics),
            "metric_counts": {k: dict(v) for k, v in self.metric_counts.items()},
            "consistency_violations": list(self.consistency_violations),
            "required_metrics": list(REQUIRED_BENCHMARK_METRICS),
            "cases": list(self.cases),
        }


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(numerator / denominator, 4)


def _build_cases() -> list[GovernanceBenchmarkCase]:
    return [
        GovernanceBenchmarkCase(
            case_id="BMK-001",
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="BMK-001",
                requested_judgment="certificate",
                proof_object_ref="PO-001",
                governance_gate_passed=True,
                reverse_trace_ref="RT-001",
                evidence_matches_claim=True,
            ),
            expected_downgrade=False,
            expected_illicit_block=False,
            expected_forbidden_detection=False,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-002",
            agent_id="agent-b",
            attempt=AdversarialAttempt(
                attempt_id="BMK-002",
                requested_judgment="certificate",
                proof_object_ref="",
                governance_gate_passed=True,
                reverse_trace_ref="RT-002",
                evidence_matches_claim=True,
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=False,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-003",
            agent_id="agent-c",
            attempt=AdversarialAttempt(
                attempt_id="BMK-003",
                requested_judgment="certificate",
                proof_object_ref="PO-003",
                governance_gate_passed=False,
                reverse_trace_ref="RT-003",
                evidence_matches_claim=True,
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=False,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-004",
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="BMK-004",
                requested_judgment="certificate",
                proof_object_ref="PO-004",
                governance_gate_passed=True,
                reverse_trace_ref="",
                evidence_matches_claim=True,
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=False,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-005",
            agent_id="agent-b",
            attempt=AdversarialAttempt(
                attempt_id="BMK-005",
                requested_judgment="certificate",
                proof_object_ref="PO-005",
                governance_gate_passed=True,
                reverse_trace_ref="RT-005",
                evidence_matches_claim=True,
                transition_tags=["model_output_as_evidence"],
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=True,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-006",
            agent_id="agent-c",
            attempt=AdversarialAttempt(
                attempt_id="BMK-006",
                requested_judgment="certificate",
                proof_object_ref="PO-006",
                governance_gate_passed=True,
                reverse_trace_ref="RT-006",
                evidence_matches_claim=True,
                transition_tags=["residual_erasure"],
                residuals=[],
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=True,
            requires_residual_preservation=True,
            trace_complete=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-007",
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="BMK-007",
                requested_judgment="certificate",
                proof_object_ref="PO-007",
                governance_gate_passed=True,
                reverse_trace_ref="RT-007",
                evidence_matches_claim=True,
                transition_tags=["silent_level_skip"],
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=True,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-008",
            agent_id="agent-b",
            attempt=AdversarialAttempt(
                attempt_id="BMK-008",
                requested_judgment="hypothesis",
                transition_tags=["emphasis_as_evidence"],
            ),
            expected_downgrade=False,
            expected_illicit_block=False,
            expected_forbidden_detection=True,
            requires_residual_preservation=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-009",
            agent_id="agent-c",
            attempt=AdversarialAttempt(
                attempt_id="BMK-009",
                requested_judgment="certificate",
                proof_object_ref="PO-009",
                governance_gate_passed=True,
                reverse_trace_ref="RT-009",
                evidence_matches_claim=True,
                residuals=["residual_conflict"],
            ),
            expected_downgrade=True,
            expected_illicit_block=True,
            expected_forbidden_detection=False,
            requires_residual_preservation=True,
            replay_event_valid=False,
        ),
        GovernanceBenchmarkCase(
            case_id="BMK-010",
            agent_id="agent-a",
            attempt=AdversarialAttempt(
                attempt_id="BMK-010",
                requested_judgment="zero",
            ),
            expected_downgrade=False,
            expected_illicit_block=False,
            expected_forbidden_detection=False,
            requires_residual_preservation=False,
        ),
    ]


def run_empirical_benchmarks(
    cases: list[GovernanceBenchmarkCase] | None = None,
) -> BenchmarkRunReport:
    benchmark_cases = cases or _build_cases()
    attempts = [
        DistributedAgentAttempt(agent_id=case.agent_id, attempt=case.attempt)
        for case in benchmark_cases
    ]
    simulation = run_distributed_governance_simulation(attempts)
    eval_map = {e.attempt_id: e for e in simulation.evaluations}

    illicit_total = 0
    illicit_blocked = 0
    forbidden_total = 0
    forbidden_detected = 0
    residual_total = 0
    residual_preserved = 0
    downgrade_total = 0
    downgrade_correct = 0
    replay_success_count = 0
    event_payloads: list[dict] = []
    case_rows: list[dict] = []
    forbidden_set = set(FORBIDDEN_TRANSITIONS)

    for i, case in enumerate(benchmark_cases, start=1):
        evaluation = eval_map[case.case_id]

        if case.expected_illicit_block:
            illicit_total += 1
            if evaluation.public_judgment != "certificate":
                illicit_blocked += 1

        forbidden_tags = [
            tag for tag in case.attempt.transition_tags if tag in forbidden_set
        ]
        if case.expected_forbidden_detection:
            forbidden_total += 1
            if any(tag in evaluation.blocked_reasons for tag in forbidden_tags):
                forbidden_detected += 1

        if case.requires_residual_preservation:
            residual_total += 1
            if bool(evaluation.residuals):
                residual_preserved += 1

        if case.expected_downgrade:
            downgrade_total += 1
            if evaluation.public_judgment == "hypothesis":
                downgrade_correct += 1

        event = {
            "request_id": f"REQ-{i:03d}" if case.replay_event_valid else "",
            "replay_id": f"RPL-{i:03d}" if case.replay_event_valid else "",
            "forbidden_transition": bool(forbidden_tags),
            "certificate_blocked": case.expected_illicit_block
            and evaluation.public_judgment != "certificate",
            "residual_preserved": bool(evaluation.residuals)
            if case.requires_residual_preservation
            else True,
            "trace_complete": case.trace_complete,
            "governance_consistent": True,
            "collapse_event": False,
            "status_code": 200 if evaluation.public_judgment != "zero" else 400,
            "execution_time_ms": 0.0,
        }
        event_payloads.append(event)
        replay_result = replay_trace_events([event])
        if replay_result.replay_success:
            replay_success_count += 1

        case_rows.append(
            {
                "case_id": case.case_id,
                "agent_id": case.agent_id,
                "requested_judgment": case.attempt.requested_judgment,
                "public_judgment": evaluation.public_judgment,
                "blocked_reasons": list(evaluation.blocked_reasons),
                "residuals": list(evaluation.residuals),
            }
        )

    governance_metrics = compute_governance_metrics(event_payloads).to_dict()
    distributed_consistency_rate = _ratio(
        max(len(benchmark_cases) - len(simulation.consistency_violations), 0),
        len(benchmark_cases),
    )

    metrics = {
        "illicit_certification_block_rate": _ratio(illicit_blocked, illicit_total),
        "forbidden_transition_detection_rate": _ratio(
            forbidden_detected, forbidden_total
        ),
        "residual_preservation_rate": _ratio(residual_preserved, residual_total),
        "replay_success_rate": _ratio(replay_success_count, len(benchmark_cases)),
        "distributed_consistency_rate": distributed_consistency_rate,
        "trace_completeness_score": round(
            float(governance_metrics["trace_completeness"]), 4
        ),
        "adversarial_downgrade_accuracy": _ratio(downgrade_correct, downgrade_total),
    }

    metric_counts = {
        "illicit_certification_block_rate": {
            "numerator": illicit_blocked,
            "denominator": illicit_total,
        },
        "forbidden_transition_detection_rate": {
            "numerator": forbidden_detected,
            "denominator": forbidden_total,
        },
        "residual_preservation_rate": {
            "numerator": residual_preserved,
            "denominator": residual_total,
        },
        "replay_success_rate": {
            "numerator": replay_success_count,
            "denominator": len(benchmark_cases),
        },
        "distributed_consistency_rate": {
            "numerator": max(len(benchmark_cases) - len(simulation.consistency_violations), 0),
            "denominator": len(benchmark_cases),
        },
        "trace_completeness_score": {
            "numerator": sum(1 for e in event_payloads if e.get("trace_complete")),
            "denominator": len(event_payloads),
        },
        "adversarial_downgrade_accuracy": {
            "numerator": downgrade_correct,
            "denominator": downgrade_total,
        },
    }

    return BenchmarkRunReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_cases=len(benchmark_cases),
        metrics=metrics,
        metric_counts=metric_counts,
        consistency_violations=list(simulation.consistency_violations),
        cases=case_rows,
    )
