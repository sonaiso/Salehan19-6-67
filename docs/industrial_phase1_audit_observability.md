# Industrial Phase 1 — Governed Audit Trail & Contract Observability

## Why this is required after Phase 0 closeout

Phase 0 froze Φ/Ω/Certificate contracts and regression gates.  
Industrial operation now requires explainability of runtime outcomes, not contract redefinition.

This layer adds observability to governed outcomes so production operators can see **why** a result was:
- allowed
- downgraded
- blocked
- suspended

It does not change the governance kernel or certificate conditions.

## Audit event model

`GovernanceAuditEvent` captures:

- `event_id`: unique in-process event identifier
- `proof_id`: proof object reference (if present)
- `input_judgment`: incoming judgment before enforcement
- `output_judgment`: final enforced public judgment
- `decision`: allowed/downgraded/blocked/suspended
- `gate`: dominant gating domain (`phi`, `omega`, `proof_object`, `governance_gate`, `residuals`, `certificate`)
- `reason_codes`: normalized machine-readable reasons
- `residuals`: residual markers preserved on the governed output
- `has_raw_text_anchor`: whether reverse trace has `raw_text_units`
- `has_reverse_trace`: whether reverse trace evidence exists
- `has_proof_object`: whether proof object exists
- `governance_gate_passed`: governance gate status
- `blocking_residuals_present`: whether blocking residuals were present
- `silent_level_skip_present`: whether silent-level-skip marker exists
- `timestamp`: optional field (left `None` in-process by default)

## Standard reason codes

The observability layer standardizes these reason codes:

- `certificate_without_reverse_trace`
- `reverse_trace_missing_raw_text`
- `certificate_without_proof_object`
- `certificate_without_governance_gate`
- `certificate_with_blocking_residuals`
- `silent_level_skip`
- `forbidden_transition_marker`
- `phi_transition_condition_unknown`
- `phi_transition_condition_failed`
- `certificate_allowed`

## Audit vs ProofObject

Audit metadata is diagnostic telemetry.  
`ProofObject` remains the formal governance artifact for certificate eligibility.

Audit does not substitute for proof validity and cannot elevate a judgment.

## Audit vs residuals

Residuals remain governance-preserved outputs that block or constrain certainty.  
Audit reason codes explain decision pathways and gate outcomes.

Residuals are part of governed state; audit is observability over that state.

## Audit must not issue certificate

Audit metadata is read-only explanatory output.  
Certificate issuance remains gated by existing Phase 0 conditions:

- allowed Φ path
- complete Ω reverse trace to `raw_text_units`
- proof object present
- governance gate passed
- no blocking residuals
- no silent level skip
- no forbidden transition marker

## Industrial deployment value

This observability layer supports:
- traceability for runtime governance outcomes
- operational diagnosis of gate failures
- incident review and post-mortem analysis
- non-invasive observability for stable APIs

Phase 0 remains contract-frozen; this is observability-only hardening.
