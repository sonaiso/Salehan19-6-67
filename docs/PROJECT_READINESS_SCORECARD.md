# Project Readiness Scorecard

## Overview

This scorecard assesses the production readiness of the MCD/NERL/FPCL/GLCFL/EIRL system across 10 dimensions. Each dimension is scored 1–5:

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Concept | Idea only, nothing working |
| 2 | Research Prototype | Experimental, cannot be relied upon |
| 3 | Working Prototype | Functions correctly, not production-safe |
| 4 | Pilot Ready | Can be used in controlled, supervised pilots |
| 5 | Production Ready | Deployable at scale with confidence |

**Current Average: 2.4/5 — Working Prototype**

> **Audit note (current-state alignment):** Earlier revisions of this scorecard
> claimed *"No REST API"*. That claim is **incorrect against the current code
> state**. A FastAPI application exists at `src/mcd/api/app.py` with v1
> versioned routes (`src/mcd/api/v1_routes.py`), observability hooks
> (`src/mcd/api/observability.py`), schema stability checks, and a dedicated
> pilot-readiness endpoint. However, the API itself declares in its module
> docstring: *"No LLM calls. No external network calls. No GraphRAG. Not
> production-ready. Pilot-ready candidate only."* The correct framing is
> therefore a three-way distinction:
>
> - **API exists** — confirmed (`src/mcd/api/app.py`, tests under
>   `tests/test_api_*.py`).
> - **API pilot-ready candidate** — declared by the code itself; gated by
>   `docs/API_PILOT_READINESS.md` and `docs/PILOT_READINESS_GATE.md`.
> - **API production-ready** — **NOT** claimed; production blockers remain
>   open per `docs/PRODUCTION_GAP_ANALYSIS.md`.
>
> Per the documentation rule established by this audit (see
> [`CURRENT_CAPABILITY_MATRIX.md`](CURRENT_CAPABILITY_MATRIX.md)), no document
> in this repository may claim *production-ready*, *fully compliant*, or
> *certificate* status without citing the specific tests and governance gates
> that prove it.

---

## 10-Dimension Scorecard

| # | Dimension | Score | Rationale |
|---|-----------|-------|-----------|
| 1 | Architecture Maturity | 3/5 | Multiple layers with clean separation. CLI works. FastAPI REST API exists at `src/mcd/api/app.py` but declares itself "Not production-ready. Pilot-ready candidate only." |
| 2 | Test Maturity | 4/5 | 600+ deterministic tests across all layers. No load/stress tests. |
| 3 | CLI Usability | 3/5 | decode, nabhani, classify, ground, evaluate-project commands work. No shell completion. |
| 4 | API Readiness | 2/5 | FastAPI REST API exists (`src/mcd/api/app.py`, `src/mcd/api/v1_routes.py`) with health, observability, schema stability, and pilot-readiness endpoints — but pilot-ready candidate only, not production. No auth/rate limiting/SLA. |
| 5 | Documentation | 3/5 | README, docs folder. No API reference or deployment guide. |
| 6 | Observability | 1/5 | No logging, metrics, or monitoring. Some print() in source. |
| 7 | Evaluation Dataset | 2/5 | 10 benchmark examples. No human annotation or calibration study. |
| 8 | Mathematical Formalization | 3/5 | Epistemic axioms implemented. No formal proof of correctness. |
| 9 | LLM Integration Safety | 2/5 | Adapters exist. No LLM output validation or injection guard. |
| 10 | Commercial Focus | 2/5 | Strong promise. No product roadmap or commercial packaging. |

---

## Blockers for Pilot Readiness

The following must be resolved before the system can be used in any controlled pilot:

1. **No REST API** — ~~prevents integration with any external system, workflow, or frontend~~ **CLOSED for "API exists"** (FastAPI app at `src/mcd/api/app.py`, tests at `tests/test_api_*.py`). The API is declared *pilot-ready candidate only* by its own module docstring; it is **not** production-ready. Remaining work is tracked under production blockers below, not as a missing API.
2. **No observability** — cannot monitor behavior, detect errors, or measure performance in production
3. **No evaluation dataset calibration** — cannot reliably measure accuracy without human-annotated gold labels
4. **No LLM output guardrails** — if this system wraps an LLM, the LLM's output is currently unvalidated

---

## Blockers for Production Readiness

Beyond pilot readiness, production requires:

- Authentication and authorization on any API
- Rate limiting and abuse protection
- Formal SLA (latency, uptime, error rate)
- Regression test suite with latency benchmarks
- Deployment automation (Docker, CI/CD pipeline to staging)
- Security review of all input handling paths

---

## 30-Day Action Plan

| Priority | Action | Responsible Area |
|----------|--------|-----------------|
| 🔴 Critical | ~~Implement FastAPI REST endpoint for `classify` and `decode`~~ **DONE** — present at `src/mcd/api/app.py`; remaining work is production hardening, not initial implementation | API |
| 🔴 Critical | Add structured logging with Python `logging` module | Observability |
| 🟡 High | Expand benchmark dataset to 50 examples | Evaluation |
| 🟡 High | Add integration tests for CLI + FPCL + NERL pipeline | Testing |
| 🟢 Medium | Add shell completion for CLI commands | CLI |
| 🟢 Medium | Generate API documentation from docstrings | Documentation |

---

## 90-Day Action Plan

| Priority | Action |
|----------|--------|
| 🔴 Critical | Complete REST API with authentication (JWT or API key) |
| 🔴 Critical | Add Prometheus metrics endpoint and Grafana dashboard |
| 🟡 High | Build Arabic demo application (web UI or Jupyter notebook) |
| 🟡 High | Run human annotation study on 100+ benchmark examples |
| 🟡 High | Formal documentation of epistemic axioms |
| 🟢 Medium | Commercial pilot with Arabic education or knowledge management system |
| 🟢 Medium | Add LLM output schema validation and injection guard |

---

## Dimension Details

### 1. Architecture Maturity (3/5)

**What works:**
- Five layers implemented: MCD, NERL, FPCL, GLCFL, EIRL
- Clean package separation with `__init__.py` in each layer
- CLI entry point connects all layers
- No LLM dependencies in deterministic classifiers

**What's missing:**
- ~~REST API~~ — present at `src/mcd/api/app.py` (pilot-ready candidate only, not production).
- Async support for concurrent requests
- Plugin/extension mechanism

---

### 2. Test Maturity (4/5)

**What works:**
- 600+ test functions across all layers
- Unit tests for core classification logic
- Deterministic tests (no flakiness)

**What's missing:**
- Load/stress tests (concurrent users)
- End-to-end integration tests (CLI → API → response)
- Benchmark latency tests

---

### 3. CLI Usability (3/5)

**What works:**
- `decode`, `nabhani`, `classify`, `ground` commands
- `evaluate-project`, `benchmark-simulation`, `readiness-score` commands
- JSON and text output modes

**What's missing:**
- Shell completion (bash/zsh/fish)
- Localized `--help` in Arabic
- Man pages

---

### 4. API Readiness (2/5)

**Current state:** A FastAPI REST application exists at `src/mcd/api/app.py`
(application factory `build_app()`), with versioned routes
(`src/mcd/api/v1_routes.py`), middleware (`src/mcd/api/middleware.py`),
observability hooks (`src/mcd/api/observability.py`), schema stability checks
(`src/mcd/api/schema_stability.py`), and a pilot-readiness endpoint. The
module docstring explicitly states: *"No LLM calls. No external network
calls. No GraphRAG. Not production-ready. Pilot-ready candidate only."*

**Evidence:**
- Code: `src/mcd/api/app.py`, `src/mcd/api/v1_routes.py`,
  `src/mcd/api/routes.py`, `src/mcd/api/health.py`,
  `src/mcd/api/observability.py`, `src/mcd/api/schema_stability.py`.
- Tests: `tests/test_api_classify.py`, `tests/test_api_v1_routes.py`,
  `tests/test_api_health.py`, `tests/test_api_observability.py`,
  `tests/test_api_pilot_readiness.py`, `tests/test_api_schema_stability.py`,
  `tests/test_api_response_envelope.py`, `tests/test_api_error_handling.py`,
  `tests/test_api_error_hardening.py`, `tests/test_api_hardening.py`,
  `tests/test_api_version.py`.

**Required for score 3 ("working API"):**
- ~~FastAPI or Flask REST endpoint~~ — present.
- ~~OpenAPI/Swagger documentation~~ — present (`/docs`, `/redoc`).
- Basic input validation — present via FastAPI schemas
  (`src/mcd/api/schemas.py`).
- Closure of any remaining contract-level residuals before raising the score
  beyond 2/5.

**Required for score 5:**
- Authentication and authorization
- Rate limiting
- Versioned API (`/v1/classify`)
- Production deployment guide

---

### 5. Documentation (3/5)

**What exists:**
- README.md with project overview
- docs/ folder with architecture documents
- Docstrings in major modules

**What's missing:**
- API reference (auto-generated from docstrings)
- Deployment guide
- Arabic-language documentation

---

### 6. Observability (1/5)

**Current state:** No logging framework. No metrics. No error tracking. Some `print()` calls in source files.

**Required for score 3:**
- Python `logging` module used throughout
- Structured log output (JSON format)
- Basic error tracking

**Required for score 5:**
- Prometheus metrics endpoint
- Distributed tracing (OpenTelemetry)
- Grafana dashboard
- Alerting rules

---

### 7. Evaluation Dataset (2/5)

**Current state:** 10 curated benchmark examples. No human annotations. No calibration study.

**Required for score 3:**
- 50+ examples with human-reviewed expected behaviors
- Calibration study (certainty scores validated against human judgments)

**Required for score 5:**
- 500+ examples across all task types
- Inter-annotator agreement study
- Domain expert validation (Islamic epistemic terms)

---

### 8. Mathematical Formalization (3/5)

**What's implemented:**
- Epistemic axioms (certainty levels, evidence types, domain separation)
- Certainty scoring functions
- Nabhani domain judgment logic

**What's missing:**
- Formal proof of correctness
- Uncertainty bounds (confidence intervals)
- Peer-reviewed mathematical specification

---

### 9. LLM Integration Safety (2/5)

**What works:**
- File adapter exists (`src/mcd/adapters/`)
- No LLM calls in deterministic classifiers (clean separation)

**What's missing:**
- LLM output schema validation
- Prompt injection guard
- Output sanitization before passing to downstream systems

---

### 10. Commercial Focus (2/5)

**What exists:**
- Clear domain: Arabic knowledge management and epistemic AI
- Working prototype that demonstrates the value proposition

**What's missing:**
- Product roadmap
- Target customer definition
- Commercial packaging (pricing, licensing, SLA)
- Demo application for prospect evaluation

---

## How to Update This Scorecard

This scorecard is generated from `src/mcd/evaluation/production_readiness.py`. To update scores:

```python
from mcd.evaluation.production_readiness import ProductionReadinessReport
report = ProductionReadinessReport.build_default()
print(f"Average: {report.average_score}/5")
print(f"Maturity: {report.maturity_level}")
```

Or via CLI:

```bash
python -m mcd.cli readiness-score --output json
```
