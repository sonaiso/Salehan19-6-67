# Bayani Verifier API

Bayani Verifier is the Arabic verification track.

## Purpose

Govern Arabic claims and model answers through:

- claim extraction
- evidence checks
- ZeroGuard
- ProofObject discipline
- reverse trace

## Contract Shape

Typical governed output contains:

- final judgment (ZERO/HYPOTHESIS/CERTIFICATE)
- evidence references
- residual and zero signals
- reverse trace

## Current State

- Core verification logic exists across specification and runtime components.
- Some paths are runtime-tested; other paths remain specification-governed.

## Related Materials

- `spec/bayani-knowledge-system.json`
- `schema/bayani-knowledge-system.schema.json`
- `docs/prompts/nabhani-mustadil-readiness.prompt.md`
