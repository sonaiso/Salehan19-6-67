# API_MINIMAL_REST.md — Phase 6 MCD REST API

## Overview

Phase 6 introduces a minimal REST API exposing the existing MCD engine stack.

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

Or with auto-reload for development:

```bash
python -m mcd.cli api --host 127.0.0.1 --port 8000 --reload
```

### Interactive docs

Once running:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Endpoints

### GET /health

Liveness probe.

**Response:**
```json
{
  "status": "ok",
  "service": "mcd-api"
}
```

---

### GET /version

Returns API version and active cognitive layers.

**Response:**
```json
{
  "version": "6.0.0",
  "service": "mcd-api",
  "layers": ["MCD", "NERL", "FPCL", "EIRL", "Industrial", "Curriculum"]
}
```

---

### POST /classify

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
  "status": "ok",
  "data": {
    "intent": "define",
    "certainty_policy": "conditional",
    "routing_engine": "nabhani",
    "sub_engines": [],
    "warnings": []
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 12.3
}
```

---

### POST /curriculum/evaluate

Runs curriculum evaluation on a profile.

**Request:**
```json
{
  "profile": "quick",
  "output_detail": "summary"
}
```

Supported profiles: `quick`, `full_curriculum`, `full_curriculum_extended`, `industrial_curriculum`

**Response:** APIResponse with `data` containing `CurriculumEvaluationReport.to_dict()`.

---

### POST /curriculum/quality-lock

Returns the curriculum quality lock status.

**Request:** (no body required)

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "ok",
  "data": {
    "status": "locked",
    "contract_score": 1.0,
    "is_locked": true,
    ...
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 45.0
}
```

---

### POST /industrial/test

Runs the industrial test suite.

**Request:**
```json
{
  "profile": "quick"
}
```

Supported profiles: `quick`, `full`

**Response:** APIResponse with `data.summary` and `data.results`.

---

### POST /pre-api/qualification

Returns the pre-API qualification gate result.

**Request:** (no body required)

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "ok",
  "data": {
    "status": "qualified_for_api_phase",
    "dimensions": [...],
    "api_score": 0.0,
    "non_api_passed": true
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 80.0
}
```

---

### POST /reasoning/evaluate

Full reasoning evaluation: classification + evidence need + certainty policy + warnings.

**Request:**
```json
{
  "text": "هل يجوز الاجتهاد في وجود النص الصريح؟",
  "include_debug": false
}
```

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "ok",
  "data": {
    "classification": {
      "intent": "judge",
      "judgment_types": {"shari": 0.8},
      "routing_engine": "nabhani",
      "sub_engines": []
    },
    "evidence_need": {"textual_evidence": 0.9},
    "certainty_policy": "conditional",
    "certainty_reason": "...",
    "warnings": []
  },
  "warnings": [],
  "errors": [],
  "execution_time_ms": 15.0
}
```

---

## Response Schema

All POST endpoints return `APIResponse`:

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string (UUID) | Unique request identifier |
| `status` | string | `"ok"` on success |
| `data` | dict | Endpoint-specific payload |
| `warnings` | list[str] | Non-fatal warnings |
| `errors` | list[str] | Error messages (empty on success) |
| `execution_time_ms` | float | Processing time in milliseconds |

---

## Error Schema

All errors return `ErrorResponse`:

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Request identifier |
| `error_code` | string | Machine-readable error code |
| `message` | string | Human-readable message |
| `details` | dict | Additional error context |

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

## Limitations

- No authentication
- No rate limiting
- No persistent logging
- No external source adapter calls (MockSourceAPI only)
- No LLM integration
- No GraphRAG
- No production deployment configuration
- Not production-ready — **pilot-ready candidate only**

---

## Testing

```bash
PYTHONPATH=src python -m pytest tests/test_api_*.py -v
```
