"""API Observability — request tracing."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field


@dataclass
class StageTrace:
    name: str
    latency_ms: float
    status: str
    details: dict = field(default_factory=dict)


@dataclass
class RequestTrace:
    request_id: str
    input_text: str
    start_time: float
    end_time: float
    total_latency_ms: float
    stages: list[StageTrace] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    final_status: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "input_text": self.input_text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_latency_ms": self.total_latency_ms,
            "stages": [
                {
                    "name": s.name,
                    "latency_ms": s.latency_ms,
                    "status": s.status,
                    "details": s.details,
                }
                for s in self.stages
            ],
            "warnings": self.warnings,
            "errors": self.errors,
            "final_status": self.final_status,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ObservabilityTracer:
    def start_trace(self, request_id: str, input_text: str) -> RequestTrace:
        now = time.time()
        return RequestTrace(
            request_id=request_id,
            input_text=input_text,
            start_time=now,
            end_time=now,
            total_latency_ms=0.0,
        )

    def finish_trace(self, trace: RequestTrace, status: str = "ok") -> None:
        trace.end_time = time.time()
        trace.total_latency_ms = (trace.end_time - trace.start_time) * 1000
        trace.final_status = status
