# Theorem Roadmap

## PR #73 — Formal Theorem Verification Track

This PR is constrained to **Phase-0 governance/formal artifacts only** and does not alter runtime behavior.

### Target obligations

1. NoIllicitCertification
2. ResidualPersistence
3. ForbiddenEscalation
4. TriadClosure
5. ReplayIntegrity

### Artifacts delivered in PR #73

- obligations file: `research/formal/theorem_obligations.json`
- proof mapping: `research/formal/proof_mapping.json`
- Lean skeleton: `research/formal/lean/`
- Coq skeleton: `research/formal/coq/`
- theorem scaffolding: `research/formal/theorem_scaffolding.json`

### Governance note

CERTIFICATE issuance remains gated by ProofObject + GovernanceGate + ReverseTrace.
Final epistemic judgments remain ZERO/HYPOTHESIS/CERTIFICATE only.

## Dependency chain after PR #73

- PR #74 → Distributed Governance Runtime
- PR #75 → Cryptographic Certification
- PR #76 → External Audit + Research Publication

PR #74 and PR #75 are downstream of the obligations + proof mapping produced in PR #73.
