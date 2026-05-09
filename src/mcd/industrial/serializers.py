"""Serializers for industrial testing objects."""
from __future__ import annotations

import json

from mcd.industrial.api_contract import SourceAPIResponse, SourceDocument, SourceQuery
from mcd.industrial.source_trust_policy import SourceTrustResult
from mcd.industrial.industrial_test_runner import IndustrialResult
from mcd.industrial.latency_benchmark import LatencyBenchmarkResult
from mcd.industrial.pilot_readiness import PilotReadinessResult


def source_response_to_dict(r: SourceAPIResponse) -> dict:
    return {
        "query_id": r.query_id,
        "status": r.status,
        "latency_ms": r.latency_ms,
        "error_message": r.error_message,
        "warnings": r.warnings,
        "documents": [
            {
                "source_id": d.source_id,
                "title": d.title,
                "content": d.content,
                "source_type": d.source_type,
                "authority_level": d.authority_level,
                "freshness": d.freshness,
                "retrieved_at": d.retrieved_at,
                "metadata": d.metadata,
            }
            for d in r.documents
        ],
    }


def industrial_result_to_dict(r: IndustrialResult) -> dict:
    return {
        "case_id": r.case_id,
        "input_text": r.input_text,
        "source_status": r.source_status,
        "source_trust_summary": r.source_trust_summary,
        "prompt_frame": r.prompt_frame,
        "evidence_status": r.evidence_status,
        "certainty_policy": r.certainty_policy,
        "epistemic_status": r.epistemic_status,
        "warnings": r.warnings,
        "forbidden_behavior_detected": r.forbidden_behavior_detected,
        "passed": r.passed,
        "score": r.score,
        "latency_ms": r.latency_ms,
        "explanation": r.explanation,
    }


def pilot_readiness_to_dict(r: PilotReadinessResult) -> dict:
    return {
        "ready_for_pilot": r.ready_for_pilot,
        "score": r.score,
        "passed_criteria": r.passed_criteria,
        "failed_criteria": r.failed_criteria,
        "blockers": r.blockers,
        "next_actions": r.next_actions,
        "conditional": r.conditional,
    }


def latency_result_to_dict(r: LatencyBenchmarkResult) -> dict:
    return {
        "total_cases": r.total_cases,
        "avg_latency_ms": r.avg_latency_ms,
        "p50_latency_ms": r.p50_latency_ms,
        "p95_latency_ms": r.p95_latency_ms,
        "max_latency_ms": r.max_latency_ms,
        "by_component": r.by_component,
        "warnings": r.warnings,
    }


def to_json(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
