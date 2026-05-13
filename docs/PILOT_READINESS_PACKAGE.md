# Pilot Readiness Package

Status: **Pilot scientific-industrial qualification package** (controlled pilot scope, **not production-certified**).

Official positioning:

> A governed epistemic and meaning-ascent platform with machine-checkable core proof fragments, ranked certificate gating, typed residual preservation, persistent audit replay, adversarial validation, and empirical readiness scoring.

## Deployment Profile

- Profile: controlled pilot only
- Runtime: governed Python runtime (`src/mcd`)
- Entry surfaces: CLI + API profiles already present in repository
- Audit requirement: immutable event log + replay trace reconstruction enabled

## Security Assumptions

- Certificate remains gated by ProofObject + GovernanceGate + ReverseTrace.
- Forbidden transitions remain blocked and downgrade to non-certificate paths.
- Residual erasure remains a blocking condition.
- This package does not claim enterprise production hardening yet.

## Audit Report

- Persistent audit backend: `src/mcd/audit/backend/persistent.py`
- Replay and forensics: `src/mcd/audit/replay.py`
- Replay integrity contract encoded in runtime snapshot output (`replay_integrity_contract`).

## Benchmark Report

- Benchmarks and readiness baselines remain in `benchmarks/` and industrial reporting modules.
- Qualification interpretation: benchmark evidence supports controlled pilot readiness, not final industrial certification.

## Known Limitations

- Runtime↔formal equivalence is bounded to explicit governed truth-table contracts.
- Replay integrity is contract-level (governed sequence consistency), not full theorem completion.
- Layer sovereignty registry is explicit and executable but remains an evolving governance registry.
- External enterprise controls (full authz hardening, large-scale deployment SLO package) remain downstream.

## Release Notes

- Added executable Runtime↔Formal equivalence truth-table artifact.
- Added explicit replay integrity contract payload (`ValidEventLog => replay-consistent judgment sequence`).
- Added layer sovereignty registry with Governor, allowed/forbidden ascent, required evidence, χ_L, MC_L, and residual rules.
- Aligned official wording to pilot qualification posture.
- Added PR #89 external pilot package docs:
  - `docs/EXTERNAL_AUDIT_PACKAGE.md`
  - `docs/PILOT_RISK_REGISTER.md`
  - `docs/PILOT_DEPLOYMENT_GUIDE.md`
  - `docs/SCIENTIFIC_VALIDATION_REPORT.md`
  - `docs/INDUSTRIAL_VALIDATION_REPORT.md`
  - `docs/KNOWN_LIMITATIONS.md`
  - `examples/pilot/`
  - `scripts/run_pilot_validation.py`
