# Current Capability Matrix

> **Purpose.** Provide a single, current-state, evidence-anchored view of what
> the repository actually implements today, what is only a contract, and what
> is not implemented yet. This document is part of the Phase 0 governance
> surface: it exists to **prevent documentation drift from becoming an
> implicit certificate**.
>
> **Scope.** Documentation audit only. This document does **not** add new
> capabilities, change Phase 0 certificate semantics, redefine Φ or Ω, or
> claim production readiness.

---

## Documentation rule (governing this matrix and the rest of `docs/`)

No document in this repository may claim **production-ready**,
**fully compliant**, or **certificate** status for any subsystem unless it
cites:

1. the concrete tests (file paths) that exercise the claim, and
2. the governance gates (`ProofObject`, `GovernanceGate`, `ReverseTrace`,
   forbidden-transition checks) that authorize the claim.

Per `docs/phase0_closeout.md` and `docs/10_FORBIDDEN_TRANSITIONS.md`, any
claim that fails this rule must be downgraded to **HYPOTHESIS** or **ZERO**.
Only **ZERO**, **HYPOTHESIS**, and **CERTIFICATE** are valid final epistemic
judgments. Forbidden transitions include, among others,
`tool_output_as_certificate_without_governance`,
`certificate_without_proof_object`,
`certificate_without_governance_gate`,
`certificate_without_reverse_trace`, `residual_erasure`, and
`silent_level_skip`.

---

## Status legend

| Status | Meaning |
|---|---|
| `implemented` | Code and tests both present; behavior exercised in the suite. |
| `partial` | Some code and tests present; non-trivial gaps remain. |
| `contract-only` | Schemas/contracts/governance gates exist; substantive runtime behavior is bounded or scaffolding-level only. |
| `not implemented` | No code path; only design intent or roadmap. |
| `unverified` | Code may exist but the audit did not confirm tests proving the claim; treat as `HYPOTHESIS` until evidenced. |

`current rank` uses the Phase 0 epistemic-judgment vocabulary: **ZERO**,
**HYPOTHESIS**, **CERTIFICATE**. A row may **only** be ranked `CERTIFICATE`
if its `evidence files` and `tests` columns together satisfy the
documentation rule above (governance gate + proof object + reverse trace
present and exercised).

---

## Matrix

| Layer | Status | Evidence files | Tests | Current rank | Residual gaps | Next required PR |
|---|---|---|---|---|---|---|
| **Phase 0 — Governance kernel** (forbidden transitions, judgment law, ProofObject, ReverseTrace, GovernanceGate) | `implemented` | `src/mcd/core/forbidden_transitions.py`, `src/mcd/core/proof_object.py`, `src/mcd/core/governance_audit.py`, `src/mcd/core/transition_governance.py`, `src/mcd/fractal_kernel/proof_object.py`, `src/mcd/fractal_kernel/reverse_trace.py`, `src/mcd/fractal_kernel/kernel_validator.py`, `docs/phase0_closeout.md`, `docs/10_FORBIDDEN_TRANSITIONS.md` | `tests/test_proof_object_reverse_trace.py`, `tests/test_kernel_validator.py`, `tests/test_cfk_reverse_trace.py`, `tests/test_certificate_pipeline_integrity.py`, `tests/test_phase0_contract_freeze.py`, `tests/test_thinking_forbidden_transitions.py`, `tests/test_math_governance_transition_contract.py` | **CERTIFICATE** (governance kernel only; gates exercised in test suite) | None blocking at the governance-kernel level itself; downstream layers still consume the kernel. | None required for Phase 0; further work belongs to downstream layers. |
| **Phase 1 — Governed serialization & public contract hardening** | `implemented` | `src/mcd/core/serialization.py`, `src/mcd/core/public_schema.py`, `src/mcd/core/public_judgment.py`, `src/mcd/core/residual_taxonomy.py`, `docs/industrial_phase1_roadmap.md` | Public-contract / serialization tests under `tests/` (e.g., `test_certificate_pipeline_integrity.py`, `test_phase0_contract_freeze.py`, `test_math_governance_transition_contract.py`) | **HYPOTHESIS** (contracts hardened; broad-suite stability tracked, but Phase 1 explicitly does not certify downstream behavior) | Per `docs/industrial_phase1_roadmap.md`, Phase 1 does **not** redefine Φ/Ω, does **not** add new theory, and does **not** weaken certificate gates. | Per-subsystem hardening PRs only when downstream layers require it. |
| **Phase 2 — Prompt-understanding payload** | `implemented` | `src/mcd/prompt_understanding/__init__.py`, `src/mcd/prompt_understanding/payload.py` | `tests/test_prompt_understanding_payload.py` | **HYPOTHESIS** (payload contract exercised; no claim of human-level understanding) | Payload-level only; does not constitute structural understanding or human-cognition simulation. | None required for the payload itself. |
| **Phase 3A — Fractal operator learning** | `partial` | `src/mcd/fractal_learning/operator_candidate.py`, `src/mcd/fractal_learning/operator_contract.py`, `src/mcd/fractal_learning/operator_registry.py`, `src/mcd/fractal_learning/failure_locator.py` | `tests/test_fractal_operator_learning.py`, and related `tests/test_fractal_*` | **HYPOTHESIS** | Operator induction is governed but bounded; no end-to-end certificate of learned-operator soundness across the full operator algebra. | Targeted PR to extend operator-induction coverage and tighten residual taxonomy linkage. |
| **Phase 3A+ — Operator composition** | `partial` | `src/mcd/fractal_learning/operator_composition.py` | `tests/test_fractal_operator_composition.py`, `tests/test_composition_function.py` | **HYPOTHESIS** | Composition contracts exist; full closure of operator-composition governance (algebraic invariants under composition) is not yet certificated. | Targeted PR to close operator-composition governance gates with explicit `ProofObject` linkage. |
| **Phase 3B — Quantitative reasoning** | `contract-only` | Quantity-extraction scaffolding under `src/mcd/quantity_extraction/`, `tests/test_quantity_mention_extraction.py` exercises extraction only. | `tests/test_quantity_mention_extraction.py` (extraction-level only) | **HYPOTHESIS** | No quantitative reasoning pipeline that composes extracted quantities through governed operators into a certificated quantitative claim. Phase 3B as a full layer is **not implemented**. | Phase 3B design PR must precede any implementation PR; must inherit Phase 0 gates and not bypass `ProofObject`/`ReverseTrace`. |
| **REST API** | `partial` | `src/mcd/api/app.py` (FastAPI app factory; declared *"Not production-ready. Pilot-ready candidate only."*), `src/mcd/api/v1_routes.py`, `src/mcd/api/routes.py`, `src/mcd/api/health.py`, `src/mcd/api/schemas.py`, `src/mcd/api/middleware.py`, `src/mcd/api/observability.py`, `src/mcd/api/schema_stability.py` | `tests/test_api_classify.py`, `tests/test_api_v1_routes.py`, `tests/test_api_health.py`, `tests/test_api_observability.py`, `tests/test_api_pilot_readiness.py`, `tests/test_api_schema_stability.py`, `tests/test_api_response_envelope.py`, `tests/test_api_error_handling.py`, `tests/test_api_error_hardening.py`, `tests/test_api_hardening.py`, `tests/test_api_version.py`, `tests/test_api_reasoning_evaluate.py` | **HYPOTHESIS** (pilot-ready candidate; production controls open per `docs/PRODUCTION_GAP_ANALYSIS.md`) | Production blockers: auth/authz, rate limiting, SLA/SLO, monitoring dashboards, load/resilience tests, security audit, release governance. | Production-hardening PRs tracked in `docs/PRODUCTION_GAP_ANALYSIS.md`; not in scope for any Phase 0 work. |
| **Observability** | `partial` | `src/mcd/observability/logging.py`, `src/mcd/observability/runtime_metrics.py`, `src/mcd/observability/prometheus/`, `src/mcd/observability/store.py`, `src/mcd/api/observability.py` | `tests/test_api_observability.py` (and adjacent) | **HYPOTHESIS** | Primitives exist; no production dashboards, no SLO instrumentation, no retention/compliance policy. | Production observability hardening PR (out of Phase 0 scope). |
| **Evaluation dataset** | `partial` | `src/mcd/evaluation/`, curated benchmark examples; see `docs/PROJECT_READINESS_SCORECARD.md` §7 for size and calibration status | `tests/test_evaluation_benchmark_dataset.py`, `tests/test_evaluation_kpi_schema.py`, `tests/test_evaluation_runner.py`, `tests/test_evaluation_report_builder.py`, `tests/test_evaluation_simulation_metrics.py`, `tests/test_evaluation_repository_audit.py`, `tests/test_evaluation_architecture_audit.py` | **HYPOTHESIS** | Limited size; no human-annotated gold labels or inter-annotator agreement study committed. | Calibration/annotation PR (out of Phase 0 scope). |
| **Production security** | `not implemented` | None — see `docs/PRODUCTION_GAP_ANALYSIS.md` for the open blocker list with `evidence_path` columns. | None proving production security closure. | **ZERO** (no closure evidence) | Auth/authz, rate limiting, security audit, release governance — all open. | Tracked exclusively in `docs/PRODUCTION_GAP_ANALYSIS.md`; not in scope for Phase 0 documentation audit. |
| **LLM proposer governance** (related: gates LLM output to evidence + reverse trace + Nabhani gate before any CERTIFICATE) | `implemented` | `src/mcd/llm_proposer/governor.py`, `src/mcd/llm_proposer/governed_payload.py`, `src/mcd/llm_proposer/trace.py`, `src/mcd/llm_proposer/verdict_mapping.py` | `tests/llm_proposer/` | **HYPOTHESIS** at the layer level (the governor itself blocks unauthorized CERTIFICATE issuance) | None blocking; governor explicitly enforces that LLM output cannot become a certificate without governance. | None required. |

---

## How to use this matrix

1. Before claiming any subsystem is "ready", locate its row and read the
   `current rank` and `residual gaps` columns.
2. If you need to **raise** a row's rank, open a PR that adds the missing
   evidence (code + tests + governance-gate linkage) and updates this matrix
   in the same PR.
3. If you **discover drift** (docs claim more than evidence supports),
   downgrade the rank in this matrix and the affected document. **Never**
   silently raise a rank.
4. This matrix is the single source of truth for current-state capability
   claims in this repository. Other documents (e.g.,
   `PROJECT_READINESS_SCORECARD.md`, `PRODUCTION_GAP_ANALYSIS.md`) must be
   consistent with it; on conflict, the matrix wins until reconciled.

---

## Audit metadata

- **Audit type.** Current-state documentation and capability audit.
- **Audit scope.** Documentation only. No runtime behavior, no Phase 0
  semantics, no new theory, no production-ready claims introduced.
- **Phase 0 governance.** This document is governed by
  `docs/phase0_closeout.md` and the forbidden-transition catalogue in
  `docs/10_FORBIDDEN_TRANSITIONS.md`. Any future edit must preserve the
  documentation rule above.
- **Source of evidence.** Direct inspection of the repository tree at the
  time of the audit (`src/mcd/api/`, `src/mcd/prompt_understanding/`,
  `src/mcd/fractal_learning/`, `src/mcd/core/`, `src/mcd/llm_proposer/`,
  `src/mcd/math_governance/`, `src/mcd/observability/`, `tests/`).
