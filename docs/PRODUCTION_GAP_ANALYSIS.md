# Production Gap Analysis

Current position: release-candidate assessment package under controlled scope.

> **Audit note (current-state alignment):** This document tracks *production*
> blockers. The repository **does** have a FastAPI REST API
> (`src/mcd/api/app.py`) declared as a *pilot-ready candidate only* by its own
> module docstring. The presence of an API does **not** by itself close any
> of the production blockers below. A blocker is only marked closed when its
> `evidence_path` cites concrete code **and** tests proving the control is in
> place; otherwise it remains open.

## Gaps to close before production

| # | Gap | Status | Evidence path |
|---|-----|--------|---------------|
| 1 | Real authentication and authorization enforcement for production deployment. | **Open** | No production-grade auth verified. Profile-gated baseline controls only (see `src/mcd/api/middleware.py`, `src/mcd/api/dependencies.py`). No closure evidence. |
| 2 | Persistent database backend policy and operational governance hardening. | **Open** | No persistent production DB policy committed. |
| 3 | Log retention, compliance, and secure archival policy. | **Open** | Logging primitives exist (`src/mcd/observability/logging.py`), but retention/compliance policy not documented. |
| 4 | Rate limiting and abuse-protection controls for exposed surfaces. | **Open** | Baseline scaffolding only; no production-grade enforcement evidence. |
| 5 | Monitoring dashboards and production alerting/SLO instrumentation. | **Open** | Metrics primitives exist (`src/mcd/observability/runtime_metrics.py`, `src/mcd/observability/prometheus/`), but no production dashboards/SLO evidence. |
| 6 | Load and resilience testing under production-like traffic. | **Open** | No load/stress test suite present. |
| 7 | Independent security audit and remediation closure. | **Open** | No external audit artifact committed. |
| 8 | External sign-off process for governed deployment risk acceptance. | **Open** | Not documented. |
| 9 | Versioned release governance with controlled rollout/release notes. | **Open** | No release-governance artifact committed for production rollout. |

> A gap moves from **Open** to **Closed** only when its `evidence_path` cites
> both the implementing code path(s) **and** the test path(s) that exercise
> it. Documentation alone does not constitute closure evidence.

## Why this remains below production certification

- Pilot and release-candidate evidence demonstrates bounded governance behavior, not full production guarantees.
- Certificate issuance constraints remain strict and cannot be bypassed.
- Open production controls must be closed before any production-certified claim.

## Documentation rule (current-state alignment)

No document in this repository may claim **production-ready**,
**fully compliant**, or **certificate** status for any subsystem unless it
cites:

1. the concrete tests (file paths) that exercise the claim, and
2. the governance gates (e.g., `ProofObject`, `GovernanceGate`,
   `ReverseTrace`) that authorize it.

Claims that fail this rule must be downgraded to **HYPOTHESIS** or **ZERO**
per the Phase 0 forbidden-transition catalogue
(`docs/10_FORBIDDEN_TRANSITIONS.md`, `docs/phase0_closeout.md`).
