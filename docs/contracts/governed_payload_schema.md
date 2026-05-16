# Governed Payload Schema (Public Contract)

## Purpose

This document defines the official public governed payload fields for Industrial Phase 1 stabilization.

Phase 0 contracts remain unchanged.

## Official fields

- `proof_id`
- `judgment`
- `proof_object_ref`
- `governance_gate_passed`
- `reverse_trace_ref`
- `reverse_trace_obj`
- `residuals`
- `forbidden_transition_markers`
- `conservation`
- `_governance_audit`

## Field notes

- `judgment` runtime values are lowercase: `zero`, `hypothesis`, `certificate`.
- `reverse_trace_obj` must include `raw_text_units` for certificate eligibility.
- `residuals` preserve governance residual markers used for downgrade/blocking.
- `forbidden_transition_markers` are governance blockers when present.
- `conservation` may carry governance pass/fail state when explicit gate field is absent.

## Audit field policy

- `_governance_audit` is optional.
- `_governance_audit` appears only when `include_audit=True`.
- Audit is non-authoritative diagnostic metadata.

## Certificate governance policy

- Certificate decisions remain governed by `public_judgment` enforcement.
- Residual taxonomy is used for diagnostics and blocking detection.
- Certificate still requires:
  - ProofObject
  - GovernanceGate pass
  - complete ReverseTrace anchored to `raw_text_units`
  - no blocking residuals

## Compatibility expectations

- Stable field names are frozen for public integration.
- New fields, if added later, must be additive and backward compatible.
