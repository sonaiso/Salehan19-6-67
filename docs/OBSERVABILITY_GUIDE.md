# Observability Guide (Release Candidate)

## Metrics endpoints

- Operational metrics are assumed to be exposed through the runtime/API deployment profile.
- Governance-relevant signals should include judgment distribution, residual-preservation signals, and replay consistency checks.

## Prometheus assumptions

- Prometheus scraping is assumed to be configured by the deployment environment.
- This repository provides governance semantics and validation flows, not full production monitoring stacks.

## Replay audit flow

1. Persist immutable governance events and trace records.
2. Reconstruct replay snapshot from event stream.
3. Verify replay_integrity_contract fields and judgment sequence consistency.
4. Preserve artifacts for audit and reverse-trace review.

## Event log integrity

- Event logs are treated as integrity-critical audit evidence.
- Any tampering risk invalidates replay confidence and blocks certificate-level claims.
- Residual and governance transitions must remain explicit and preserved.

## Runtime readiness signals

- Required signals for release-candidate assessment:
  - pilot validation report available
  - runtime-formal equivalence artifact check passes
  - replay integrity contract check passes
  - layer sovereignty registry check passes
  - formal theorem track contract check passes
  - repository integrity and CLI dispatch integrity checks pass
