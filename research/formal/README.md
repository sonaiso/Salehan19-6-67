# Formal Scientific Validation Scaffolding

This folder hosts the formal theorem scaffolding for governance certification.

Current scaffolded targets:

- no illicit certification
- monotonicity boundaries
- residual persistence
- forbidden escalation
- triad closure
- replay integrity

Phase-0 scope for PR #73/PR #74:

- governance/formal artifacts only
- no runtime behavior change
- Lean includes a minimal machine-checkable core model for judgment/certificate gating
- Coq remains skeleton-only and is not proof completion

Final epistemic judgments policy:

- ZERO
- HYPOTHESIS
- CERTIFICATE

All theorem work remains governed by:

- no certificate without ProofObject
- no certificate without GovernanceGate
- no certificate without ReverseTrace
