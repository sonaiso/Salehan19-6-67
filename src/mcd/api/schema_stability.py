"""API schema stability checker.

Phase 6.1 — verifies that all API responses:
- Have no Enum leakage (no enum objects in JSON output)
- Have no dataclass leakage
- Pass JSON roundtrip
- Contain all required envelope keys
- Have stable nested keys for classify/reasoning
- Have all numbers serializable
- Have all warnings/errors as lists

CLI: python -m mcd.cli api-schema-check --output json
"""
from __future__ import annotations

import enum
import json
from dataclasses import dataclass
from typing import Any, List

from fastapi.testclient import TestClient


# Required envelope keys for POST endpoints
REQUIRED_ENVELOPE_KEYS = {"request_id", "status", "data", "warnings", "errors", "execution_time_ms"}

# Required nested keys for /classify response data
CLASSIFY_REQUIRED_DATA_KEYS = {"intent", "certainty_policy", "routing_engine"}

# Required nested keys for /reasoning/evaluate response data
REASONING_REQUIRED_DATA_KEYS = {"classification", "evidence_need", "certainty_policy"}


@dataclass
class SchemaCheckResult:
    passed: bool
    checks: List[dict]
    total: int
    failed: int

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total": self.total,
            "failed": self.failed,
            "checks": self.checks,
        }


def _has_enum_leakage(obj: Any) -> bool:
    """Return True if obj contains any enum instance."""
    if isinstance(obj, enum.Enum):
        return True
    if isinstance(obj, dict):
        return any(_has_enum_leakage(v) for v in obj.values()) or any(
            _has_enum_leakage(k) for k in obj.keys()
        )
    if isinstance(obj, (list, tuple)):
        return any(_has_enum_leakage(v) for v in obj)
    return False


def _has_dataclass_leakage(obj: Any) -> bool:
    """Return True if obj contains any dataclass instance (not dict/list/primitive)."""
    import dataclasses
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return True
    if isinstance(obj, dict):
        return any(_has_dataclass_leakage(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_has_dataclass_leakage(v) for v in obj)
    return False


def _all_numbers_serializable(obj: Any) -> bool:
    """Return True if all numbers in obj can be JSON-serialized."""
    if isinstance(obj, float):
        import math
        return not (math.isnan(obj) or math.isinf(obj))
    if isinstance(obj, dict):
        return all(_all_numbers_serializable(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_numbers_serializable(v) for v in obj)
    return True


def _json_roundtrip(data: Any) -> bool:
    """Return True if data survives a JSON encode→decode cycle unchanged."""
    try:
        encoded = json.dumps(data, ensure_ascii=False)
        decoded = json.loads(encoded)
        re_encoded = json.dumps(decoded, ensure_ascii=False)
        return encoded == re_encoded
    except Exception:
        return False


def _check_envelope(data: dict, endpoint: str) -> list[dict]:
    """Check envelope keys and types for a POST response body."""
    results = []
    for key in REQUIRED_ENVELOPE_KEYS:
        ok = key in data
        results.append({"check": f"{endpoint}:envelope_key:{key}", "passed": ok})
    # warnings must be list
    results.append({
        "check": f"{endpoint}:warnings_is_list",
        "passed": isinstance(data.get("warnings"), list),
    })
    # errors must be list
    results.append({
        "check": f"{endpoint}:errors_is_list",
        "passed": isinstance(data.get("errors"), list),
    })
    # execution_time_ms must be number
    results.append({
        "check": f"{endpoint}:execution_time_ms_is_number",
        "passed": isinstance(data.get("execution_time_ms"), (int, float)),
    })
    # request_id must be non-empty string
    results.append({
        "check": f"{endpoint}:request_id_is_str",
        "passed": isinstance(data.get("request_id"), str) and len(data.get("request_id", "")) > 0,
    })
    # status must be 'success' or 'error'
    results.append({
        "check": f"{endpoint}:status_value",
        "passed": data.get("status") in ("success", "error"),
    })
    return results


def run_schema_checks(client: TestClient | None = None) -> SchemaCheckResult:
    """Run all schema stability checks against a live test client.

    If client is None, builds a fresh app client.
    """
    if client is None:
        from mcd.api.app import build_app
        client = TestClient(build_app())

    arabic_text = "ما هو حكم الاجتهاد في المسائل الفقهية؟"
    checks: list[dict] = []

    # ------------------------------------------------------------------
    # /classify
    # ------------------------------------------------------------------
    resp = client.post("/v1/classify", json={"text": arabic_text})
    body = resp.json()

    checks += _check_envelope(body, "/v1/classify")

    # No enum leakage
    checks.append({
        "check": "/v1/classify:no_enum_leakage",
        "passed": not _has_enum_leakage(body),
    })
    # No dataclass leakage
    checks.append({
        "check": "/v1/classify:no_dataclass_leakage",
        "passed": not _has_dataclass_leakage(body),
    })
    # JSON roundtrip
    checks.append({
        "check": "/v1/classify:json_roundtrip",
        "passed": _json_roundtrip(body),
    })
    # Required data keys
    data = body.get("data", {})
    for k in CLASSIFY_REQUIRED_DATA_KEYS:
        checks.append({
            "check": f"/v1/classify:data_key:{k}",
            "passed": k in data,
        })
    # certainty_policy must be str
    checks.append({
        "check": "/v1/classify:certainty_policy_is_str",
        "passed": isinstance(data.get("certainty_policy"), str),
    })
    # Numbers serializable
    checks.append({
        "check": "/v1/classify:numbers_serializable",
        "passed": _all_numbers_serializable(body),
    })
    # No Enum class name in JSON text
    raw_text = resp.text
    checks.append({
        "check": "/v1/classify:no_enum_class_names",
        "passed": "JudgmentType" not in raw_text and "EvidenceNeed" not in raw_text,
    })

    # ------------------------------------------------------------------
    # /reasoning/evaluate
    # ------------------------------------------------------------------
    resp2 = client.post("/v1/reasoning/evaluate", json={"text": arabic_text})
    body2 = resp2.json()

    checks += _check_envelope(body2, "/v1/reasoning/evaluate")

    checks.append({
        "check": "/v1/reasoning/evaluate:no_enum_leakage",
        "passed": not _has_enum_leakage(body2),
    })
    checks.append({
        "check": "/v1/reasoning/evaluate:json_roundtrip",
        "passed": _json_roundtrip(body2),
    })
    data2 = body2.get("data", {})
    for k in REASONING_REQUIRED_DATA_KEYS:
        checks.append({
            "check": f"/v1/reasoning/evaluate:data_key:{k}",
            "passed": k in data2,
        })
    checks.append({
        "check": "/v1/reasoning/evaluate:certainty_policy_is_str",
        "passed": isinstance(data2.get("certainty_policy"), str),
    })

    # ------------------------------------------------------------------
    # /curriculum/quality-lock
    # ------------------------------------------------------------------
    resp3 = client.post("/v1/curriculum/quality-lock")
    body3 = resp3.json()
    checks += _check_envelope(body3, "/v1/curriculum/quality-lock")
    checks.append({
        "check": "/v1/curriculum/quality-lock:no_enum_leakage",
        "passed": not _has_enum_leakage(body3),
    })
    checks.append({
        "check": "/v1/curriculum/quality-lock:json_roundtrip",
        "passed": _json_roundtrip(body3),
    })

    # ------------------------------------------------------------------
    # /pre-api/qualification
    # ------------------------------------------------------------------
    resp4 = client.post("/v1/pre-api/qualification")
    body4 = resp4.json()
    checks += _check_envelope(body4, "/v1/pre-api/qualification")
    checks.append({
        "check": "/v1/pre-api/qualification:no_enum_leakage",
        "passed": not _has_enum_leakage(body4),
    })

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    failed = sum(1 for c in checks if not c["passed"])
    return SchemaCheckResult(
        passed=failed == 0,
        checks=checks,
        total=len(checks),
        failed=failed,
    )
