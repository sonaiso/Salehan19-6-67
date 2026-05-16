# Industrial Phase 1 Serialization Versioning

## Why this is required after public API stabilization

After #122, public governed payload field names are stable for downstream consumers.
The next risk is temporal drift: payload shape evolution over time without explicit version identity.
Serialization versioning closes that gap by making payload version explicit and enforceable.

## Governed payload schema version

- `schema_version` identifies the governed payload schema version.
- Current value: `1.0` (`GOVERNED_PAYLOAD_SCHEMA_VERSION`).
- `contract_version` is also emitted by serialization helpers as a stable contract marker (`1.0`).

## Governance audit schema version

- `_governance_audit` remains optional and non-authoritative.
- When audit metadata is present, `audit_schema_version` is emitted.
- Current value: `1.0` (`GOVERNANCE_AUDIT_SCHEMA_VERSION`).

## Residual taxonomy schema version

- Residual taxonomy classification is versioned with `residual_taxonomy_version`.
- Current value: `1.0` (`RESIDUAL_TAXONOMY_SCHEMA_VERSION`).
- This allows downstream audit and residual pipelines to track taxonomy compatibility.

## Backward compatibility policy

- Versioning changes are additive and do not alter final judgment vocabulary.
- Final public judgments remain: `zero`, `hypothesis`, `certificate`.
- Unknown or missing schema versions are treated as blocker residuals during validation.
- Deserialization never upgrades a non-certificate payload into certificate.

## Unsupported version behavior

- Unknown `schema_version` emits `unsupported_schema_version`.
- Missing `schema_version` emits `missing_schema_version`.
- Both are blocker residuals and prevent certificate survival after governed enforcement.

## Certificate safety rules during deserialization

- Certificate still requires ProofObject, GovernanceGate, complete ReverseTrace anchored by `raw_text_units`, and no blocking residuals.
- Deserialization validates serialization safety and appends residuals such as:
  - `serialization_missing_raw_text_units`
  - `serialization_payload_invalid`
- Any blocker residual causes downgrade to `hypothesis` under existing governance gates.
