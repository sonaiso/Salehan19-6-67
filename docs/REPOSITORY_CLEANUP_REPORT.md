# Repository Cleanup Report

## Scope

This cleanup focused on repository integrity hardening, duplicate/drift detection, formal-track reference validation, and CI hygiene without intentionally changing runtime behavior.

## What was cleaned

1. Repaired `src/mcd/murab/exception_irab_engine.py` from a stale non-Python artifact into a valid minimal module so syntax checks are stable.
2. Added `tests/test_cli_dispatch_integrity.py` to guard against:
   - duplicate CLI command registrations
   - registered commands missing dispatch coverage
3. Added `tests/test_repository_integrity.py` to guard:
   - duplicate top-level function/class definitions
   - duplicate top-level test names
   - theorem obligation ID uniqueness
   - proof mapping obligation uniqueness and parity with obligations
   - proof mapping references to real files, tests, and Lean theorem/def tokens
4. Fixed stale formal mapping reference for `ReplayIntegrity`:
   - from `src/mcd/governance/event_sourcing.py` (nonexistent)
   - to `src/mcd/audit/backend/persistent.py` (actual implementation)
5. Simplified duplicate file-existence checks in `.github/workflows/formal-theorem-track.yml` while preserving required formal artifact verification.

## What was intentionally left unchanged

1. Certificate logic and public judgment contracts.
2. Rank calculus and residual calculus semantics.
3. Lean theorem meanings and proof boundaries.
4. Existing CLI command behavior and output shapes.
5. Existing governance gate rules and reverse-trace requirements.

## Invariants preserved

1. Public final judgment triad remains: `ZERO / HYPOTHESIS / CERTIFICATE`.
2. No public `SUSPEND` final judgment introduced.
3. Certificate gating requirements remain unchanged:
   - ProofObject
   - GovernanceGate
   - ReverseTrace
   - evidence-match requirement
   - rank and forbidden-transition constraints
   - no residual erasure
4. Formal fallback remains contract-only when Lean is unavailable.

## Tests added

1. `tests/test_cli_dispatch_integrity.py`
2. `tests/test_repository_integrity.py`

## Risky areas discovered

1. The repository had a stale artifact in `src/mcd/murab/exception_irab_engine.py` that can silently break syntax tooling; this is now repaired.
2. CLI command surface is broad; future additions should update dispatch paths and integrity tests together.

## Future cleanup candidates

1. Expand AST integrity checks to include duplicate constants/enums with divergent semantics.
2. Add stricter static checks for command alias deprecation policy across docs and CLI help text.
3. Add an optional CI job for `compileall` to catch non-Python artifacts early.
