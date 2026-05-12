# Formal Proofs Baseline

This folder tracks formalization artifacts for:

- NoIllicitCertification
- ResidualPersistence
- ForbiddenEscalation
- TriadClosure
- ReplayIntegrity

Final epistemic judgments policy:

- ZERO
- HYPOTHESIS
- CERTIFICATE

PR #73 is a Phase-0 formalization bridge (obligations/mapping/scaffolds).
PR #74 adds a minimal machine-checkable core for judgment/certificate gating only.
Machine-checked proof completion of the full project remains deferred.

Planned sequence:
- PR #74: Minimal Machine-Checkable Core (judgment + certificate gating)
- PR #75: Rank Soundness + typed residual foundations
- PR #76: Replay Integrity formalization
