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

## PR #74 — Minimal Machine-Checkable Core

This stage formalizes only the public-judgment and certificate-gating core:

- `research/formal/lean/CoreJudgment.lean`
- `research/formal/lean/NoIllicitCertification.lean`
- `research/formal/lean/TriadClosure.lean`

Theorems targeted in this minimal core:

- triad_closure
- no_illicit_certification
- missing_gate_blocks_certificate
- forbidden_transition_blocks_certificate
- residual_erasure_blocks_certificate
- complete_gates_enable_certificate (limited liveness)

Claim boundary:

- machine-checkable core only
- no full-project proof claim

## PR #75 — Rank Soundness & Typed Residual Calculus

This stage extends the core with a minimal formal rank/residual layer:

- `research/formal/lean/RankSoundness.lean`
- `research/formal/lean/TypedResiduals.lean`
- `research/formal/lean/ResidualCalculus.lean`

Theorems targeted in this stage:

- rank_soundness
- insufficient_rank_blocks_certificate
- residual_persistence
- rank_gap_blocks_certificate
- missing_evidence_blocks_certificate
- residual_erasure_blocks_certificate
- unresolved_conflict_blocks_certificate

Claim boundary:

- minimal formal rank/residual extension only
- no full-project proof completion
- no consciousness or AGI claim
- no complete semantic algebra claim

## Dependency chain after PR #75

- PR #76 → Replay integrity formalization
- PR #77 → Runtime-to-formal equivalence mapping

PR #76+ are downstream of the obligations + proof mapping produced in PR #73 and core model in PR #74, with PR #75 introducing rank/residual formal contracts as the next downstream layer.
