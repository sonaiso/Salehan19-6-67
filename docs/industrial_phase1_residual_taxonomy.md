# Industrial Phase 1 — Residual Taxonomy

## Purpose

This document defines the typed residual taxonomy used by the governed output contract and governance audit observability.

The taxonomy is operational and machine-readable, while preserving Phase 0 governance invariants:

- Mind precedes language
- No certificate without ProofObject
- No certificate without GovernanceGate
- No certificate without ReverseTrace
- No residual erasure
- No silent level skip

## Strict separation

The runtime now enforces strict separation between:

1. `reason_code`  
   The primary reason emitted by Φ / Ω / gate checks (for example: `certificate_without_proof_object`).

2. `residual_spec`  
   Typed classification of a reason code:
   - `family`
   - `severity`
   - `blocks_certificate`
   - `default_message`
   - `remediation_hint`

3. `audit_event`  
   Non-authoritative diagnostic telemetry that explains outcomes.

`audit_event` does not issue judgments and must be derived from classified `reason_code` values.

## Runtime module

Implementation lives in:

- `src/mcd/core/residual_taxonomy.py`

Main API:

- `classify_residual(code) -> ResidualSpec`
- `classify_residuals(codes) -> list[ResidualSpec]`
- `has_blocking_residuals(codes) -> bool`
- `blocking_residuals(codes) -> list[ResidualSpec]`

Default safety policy:

- Unknown residuals are classified as `family=unknown`, `severity=blocker`, `blocks_certificate=True`.

## Integration points

### 1) Public judgment certificate gate

`src/mcd/core/public_judgment.py` now uses taxonomy-aware blocking checks for existing residuals:

- if residuals contain at least one blocking residual, `certificate_with_blocking_residuals` is emitted
- certificate is downgraded to `hypothesis`

### 2) Governance audit enrichment

`src/mcd/core/governance_audit.py` now enriches `_governance_audit` with:

- `residual_families`
- `residual_severities`
- `blocking_residuals`
- `remediation_hints`

Audit remains diagnostic only and cannot elevate public judgment.

## Test coverage

Added:

- `tests/test_residual_taxonomy.py`

Updated:

- `tests/test_governance_audit.py`

Coverage verifies:

- known classification
- unknown-as-blocker behavior
- non-blocking informational code (`certificate_allowed`)
- blocking detection
- audit enrichment fields

## Contract safety

This change is observability and governance-hardening oriented.
It does not alter the public final judgment set:

- `ZERO`
- `HYPOTHESIS`
- `CERTIFICATE`

No fourth final status is introduced.
