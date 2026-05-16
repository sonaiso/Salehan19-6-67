# Industrial Phase 1 — Public Governance API

## Scope

Phase 0 remains contract-frozen.  
This document stabilizes the public governance API surface after Φ/Ω closeout, audit observability, and residual taxonomy integration.

Conceptual labels may appear as `ZERO/HYPOTHESIS/CERTIFICATE`; runtime payload values stay lowercase: `zero/hypothesis/certificate`.

## Stable public API

### `enforce_governed_output_contract(payload, *, include_audit=False)`

- **Purpose**: Normalize governed output to public judgment contract and enforce certificate gates.
- **Inputs**:
  - `payload: dict[str, Any]`
  - `include_audit: bool = False`
- **Outputs**:
  - governed payload with normalized public judgments.
- **Stable fields**:
  - `judgment`, `proof_id`, `proof_object_ref`, `governance_gate_passed`, `reverse_trace_ref`, `reverse_trace_obj`, `residuals`.
- **Optional fields**:
  - `_governance_audit` (only when `include_audit=True`).
- **Internal-only fields**:
  - `internal_state` is enforcement input and not a public judgment vocabulary.
- **Certificate behavior**:
  - must downgrade certificate when ProofObject, GovernanceGate, or raw_text-anchored ReverseTrace is missing, or when blocking residuals remain.
- **Backward compatibility**:
  - public judgment triad and certificate gates are frozen.
  - audit metadata must remain optional and non-authoritative.

### `classify_residual(code)`

- **Purpose**: Convert residual code into typed `ResidualSpec`.
- **Inputs**: `code: str`
- **Outputs**: `ResidualSpec`
- **Stable fields** (`ResidualSpec`):
  - `code`, `family`, `severity`, `blocks_certificate`, `default_message`, `remediation_hint`.
- **Optional fields**:
  - `remediation_hint` may be `None`.
- **Internal-only fields**:
  - registry internals are not API contract.
- **Certificate behavior**:
  - unknown residuals default to blocker.
- **Backward compatibility**:
  - unknown-as-blocker default is contract-safe baseline.

### `classify_residuals(codes)`

- **Purpose**: Batch classify residual codes.
- **Inputs**: `codes: Sequence[str]`
- **Outputs**: `list[ResidualSpec]` preserving input order.
- **Stable fields**: same as `classify_residual`.
- **Optional fields**: `remediation_hint`.
- **Internal-only fields**: registry structure.
- **Certificate behavior**: classification supports blocker detection, not judgment issuance.
- **Backward compatibility**: function remains importable from public core namespace.

### `has_blocking_residuals(codes)`

- **Purpose**: Detect whether any residual blocks certificate.
- **Inputs**: `codes: Sequence[str]`
- **Outputs**: `bool`
- **Stable fields**: N/A
- **Optional fields**: N/A
- **Internal-only fields**: taxonomy lookup internals.
- **Certificate behavior**: `True` must block certificate.
- **Backward compatibility**: remains deterministic and taxonomy-driven.

### `GovernanceAuditEvent`

- **Purpose**: Non-authoritative diagnostic event describing governance outcome.
- **Inputs**: constructed via governance audit builder.
- **Outputs**: dataclass and `to_dict()` projection.
- **Stable fields**:
  - `event_id`, `proof_id`, `input_judgment`, `output_judgment`, `decision`, `gate`, `reason_codes`, `residuals`, `has_raw_text_anchor`, `has_reverse_trace`, `has_proof_object`, `governance_gate_passed`, `blocking_residuals_present`, `residual_families`, `residual_severities`, `blocking_residuals`, `remediation_hints`, `silent_level_skip_present`, `timestamp`.
- **Optional fields**:
  - `timestamp` may be `None`.
- **Internal-only fields**:
  - event construction heuristics are internal.
- **Certificate behavior**:
  - audit explains decision only; never issues certificate.
- **Backward compatibility**:
  - event remains additive and non-authoritative.

### `ResidualSpec`

- **Purpose**: Typed residual contract for diagnostics and gating support.
- **Inputs**: returned by taxonomy APIs.
- **Outputs**: immutable residual descriptor.
- **Stable fields**:
  - `code`, `family`, `severity`, `blocks_certificate`, `default_message`, `remediation_hint`.
- **Optional fields**:
  - `remediation_hint`.
- **Internal-only fields**:
  - registry placement/ordering.
- **Certificate behavior**:
  - `blocks_certificate=True` contributes to certificate downgrade.
- **Backward compatibility**:
  - existing fields are stable; future extension should be additive.

## Deprecated/forbidden API patterns

- Do not treat `_governance_audit` as authoritative judgment source.
- Do not infer certificate allowance from non-empty audit metadata.
- Do not bypass `public_judgment` certificate gates.
