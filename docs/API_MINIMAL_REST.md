# API_MINIMAL_REST.md — Phase 6.1 MCD REST API

## Overview

Phase 6.1 hardens the Minimal REST API with versioned routes, a unified response envelope, schema stability, and a pilot readiness endpoint.

- **No LLM calls**
- **No external network calls**
- **No GraphRAG**
- **No auth (TODO before production)**
- **No rate limiting (TODO before production)**
- **Status: Pilot-ready candidate only — NOT production-ready**

---

## How to Run

### Requirements

```bash
pip install fastapi uvicorn httpx
```

### Start the server

```bash
python -m mcd.cli api --host 127.0.0.1 --port 8000
```

### Interactive docs

Once running:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## API Versioning (Phase 6.1)

All canonical routes are now under `/v1/`. Legacy unversioned routes remain as backward-compatible aliases.

### Canonical (documented) routes:

- `GET  /v1/health`
- `GET  /v1/version`
- `POST /v1/classify`
- `POST /v1/curriculum/evaluate`
- `POST /v1/curriculum/quality-lock`
- `POST /v1/industrial/test`
- `POST /v1/pre-api/qualification`
- `POST /v1/reasoning/evaluate`
- `GET  /v1/pilot/readiness`  ← new in Phase 6.1

### Legacy aliases (backward-compatible):

- `GET  /health`, `GET /version`
- `POST /classify`, etc.

---

## Unified Response Envelope (Phase 6.1)

All POST endpoints return a unified envelope:

```json
{
  "request_id": "uuid-...",
  "status": "success",
  "data": { ... },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 12.3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string (UUID) | Unique request identifier |
| `status` | string | `"success"` on success, `"error"` on error |
| `data` | dict | Endpoint-specific payload |
| `warnings` | list[str] | Non-fatal warnings |
| `errors` | list | Structured error list (empty on success) |
| `execution_time_ms` | float | Processing time in milliseconds |

**Note:** `status` is now `"success"` (not `"ok"` as in Phase 6.0).

---

## Endpoints

### GET /v1/health

Liveness probe.

**Response:**
```json
{
  "status": "ok",
  "service": "mcd-api",
  "version": "v1"
}
```

---

### GET /v1/version

Returns API version and active cognitive layers.

**Response:**
```json
{
  "version": "6.1.0",
  "api_version": "v1",
  "service": "mcd-api",
  "layers": ["MCD", "NERL", "FPCL", "EIRL", "Industrial", "Curriculum"]
}
```

---

### POST /v1/classify

Runs FPCL classification on Arabic text.

**Request:**
```json
{
  "text": "ما هو حكم الاجتهاد في المسائل الفقهية؟",
  "include_debug": false
}
```

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "success",
  "data": {
    "intent": "define",
    "certainty_policy": "conditional",
    "routing_engine": "nabhani",
    "sub_engines": []
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 12.3
}
```

---

### POST /v1/curriculum/evaluate

Runs curriculum evaluation on a profile.

**Request:**
```json
{
  "profile": "full_curriculum",
  "output_detail": "summary"
}
```

Supported profiles: `full_curriculum`, `full_curriculum_extended`, `industrial_curriculum`, `basic_reality`, `relational_reasoning`, `evidence_certainty`, `mixed_reasoning`, `adversarial`

---

### POST /v1/curriculum/quality-lock

Returns the curriculum quality lock status.

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "success",
  "data": {
    "status": "locked",
    "contract_score": 1.0,
    "is_locked": true
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 45.0
}
```

---

### POST /v1/industrial/test

Runs the industrial test suite.

Supported profiles: `quick`, `full`

---

### POST /v1/pre-api/qualification

Returns the pre-API qualification gate result.

---

### POST /v1/reasoning/evaluate

Full reasoning evaluation: classification + evidence need + certainty policy.

---

### GET /v1/pilot/readiness (new in Phase 6.1)

Returns pilot readiness assessment.

**Response:**
```json
{
  "status": "conditional_candidate",
  "production_ready": false,
  "blockers_before_production": ["No authentication implemented", "..."],
  "api_implemented": true,
  "quality_lock": "locked",
  "tests_verified": false,
  "warnings": [
    "tests_pass must be verified by CI — cannot be hardcoded true"
  ]
}
```

**Important:**
- `production_ready` is ALWAYS `false` in Phase 6.1
- `tests_verified` is `false` — cannot be set to `true` without real CI artifact confirmation

---

## Error Schema

All errors return a structured error response (no stack traces):

```json
{
  "request_id": "uuid-...",
  "error_code": "INVALID_INPUT",
  "message": "...",
  "details": {}
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INVALID_INPUT` | 422 | Blank or semantically invalid input |
| `VALIDATION_ERROR` | 422 | Pydantic schema validation failed |
| `UNSUPPORTED_PROFILE` | 400 | Unknown profile name |
| `ENGINE_EXECUTION_ERROR` | 500 | Internal engine failure |
| `SCHEMA_SERIALIZATION_ERROR` | 500 | JSON serialization failed |
| `INTERNAL_ERROR` | 500 | Unexpected internal error |

---

## Headers

Every response includes:
- `X-Request-ID`: UUID for request tracing
- `X-Execution-Time-Ms`: Processing time in milliseconds

---

## Schema Stability

Run the schema stability checker:

```bash
python -m mcd.cli api-schema-check --output json
```

Verifies:
- No Enum leakage
- No dataclass leakage
- JSON roundtrip
- All required envelope keys
- All numbers serializable
- All warnings/errors lists

---

## Testing

```bash
PYTHONPATH=src python -m pytest tests/test_api_*.py -v
```

New Phase 6.1 test files:
- `tests/test_api_v1_routes.py`
- `tests/test_api_response_envelope.py`
- `tests/test_api_error_hardening.py`
- `tests/test_api_schema_stability.py` (extended)
- `tests/test_api_observability.py`
- `tests/test_api_pilot_readiness.py`

---

## Limitations

- No authentication
- No rate limiting
- No persistent logging
- No external source adapter calls (MockSourceAPI only)
- No LLM integration
- No GraphRAG
- No production deployment configuration
- Not production-ready — **pilot-ready candidate only**
