# Industrial Phase 1 Roadmap (Governance Kernel Hardening)

## Scope
Industrial Phase 1 hardens existing governance contracts for production readiness. It does not redefine Φ or Ω.

## 1) Contract freeze
- Freeze Φ/Ω/Certificate gate contracts as non-breakable invariants.
- Require compatibility guards for any future change touching these contracts.

## 2) Public API stabilization
- Publish stable input/output contracts for governed judgment APIs.
- Prevent silent field drift in judgment, trace, and residual payloads.

## 3) Test hardening
- Keep regression locks for certificate gating.
- Add explicit anti-regression tests for forbidden transitions and silent-level-skip.
- Maintain deterministic tri-state Φ tests.

## 4) Serialization compatibility
- Lock serialization fields for reverse trace payloads.
- Preserve `raw_text_units` across serialization round trips.

## 5) Observability and audit logs
- Standardize governance event logs for certificate decisions.
- Ensure downgrade reasons are emitted as residual markers.

## 6) Error taxonomy
- Normalize certificate-blocking errors into stable residual families.
- Separate blocking governance failures from informational warnings.

## 7) Performance baseline
- Define baseline latency/throughput for governance-critical paths.
- Track performance drift via benchmark fixtures.

## 8) CI quality gates
- Enforce tests for Φ/Ω and certificate gates on every PR.
- Keep anti-regression checks required before merge.

## 9) Release/versioning plan
- Mark boundary release as `phase0-governance-kernel`.
- Use semantic version updates only for compatible hardening changes.

## 10) Minimal production integration path
- Expose stable CLI/API path for governed judgment execution.
- Integrate evidence, reverse trace, and gate outcomes into auditable outputs.

## Non-goals
- No new theoretical layers.
- No weakening of existing governance gates.
- No redefinition of final public judgments.
