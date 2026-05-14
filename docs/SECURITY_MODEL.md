# Security Model (Release Candidate Scope)

Status: controlled deployment assessment package (**not production-certified**).

## Authentication assumptions

- Pilot-facing surfaces assume trusted operators and controlled access context.
- No claim of enterprise identity federation or hardened multi-tenant IAM.
- Any certificate path remains blocked without ProofObject + GovernanceGate + ReverseTrace.

## Authorization boundaries

- Governance boundaries are preserved by epistemic triad closure: ZERO/HYPOTHESIS/CERTIFICATE.
- No silent level skip and no residual erasure are allowed.
- Certificate escalation is blocked when forbidden transitions are detected.

## API exposure assumptions

- API/CLI are treated as controlled pilot interfaces, not open public production surfaces.
- Deployment assumes upstream network controls and controlled ingress.
- Public outputs remain bounded to governed claims and documented limitations.

## Secret handling

- Secrets are expected via deployment environment controls and must not be committed.
- Release-candidate package does not claim full enterprise secret lifecycle automation.
- Audit and validation artifacts must avoid sensitive credential content.

## Audit log sensitivity

- Event and trace logs can contain operationally sensitive metadata and must be access-controlled.
- Replay artifacts are integrity-critical and must remain immutable/auditable.
- Log handling must preserve residual and governance evidence semantics.

## Threat model

Primary threats in current scope:

- Unauthorized certificate escalation attempts.
- Governance bypass attempts (missing proof/gate/reverse trace).
- Replay tampering or event-log integrity loss.
- Silent residual removal or silent layer jump.
- Over-claiming pilot outputs as production guarantees.

## Known security gaps

- Production-grade authn/authz integration is not complete.
- Full external penetration testing and security audit are pending.
- Production log retention/compliance controls are not fully packaged.
- Hardened rate limiting and operational abuse controls remain downstream.
