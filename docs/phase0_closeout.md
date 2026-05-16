# Phase 0 Closeout

## Purpose of Phase 0
Phase 0 established the executable governance kernel that separates analysis from proof and enforces epistemic judgment law.

## What Φ proves
Φ is the forward transition contract implemented as `TransitionInput(U, P, L, R, G, C, W, X)` and `TransitionOutput(U', judgment, known, passed, residuals)`.

Tri-state behavior is fixed:
- `C is None` -> suspended, `known=0`, `passed=0`, residual `transition_condition_unknown`
- `C is False` -> blocked, `known=1`, `passed=0`, residual `transition_condition_failed`
- `C is True` -> allowed, `known=1`, `passed=1`, no residuals

## What Ω proves
Ω is the reverse trace proof path from final judgment back to source anchors. It proves backward traceability and anti-jump recoverability.

## Why `raw_text_units` is mandatory
`raw_text_units` is the canonical reverse-trace anchor. Without it, reverse trace is incomplete and cannot support certificate issuance.

## What Certificate means
`Certificate` is the governed final judgment and can only be issued when forward validity, backward traceability, proof object, governance gate, and residual-clear conditions all hold.

## Forbidden transitions
The following markers are blocked for certification, including but not limited to:
- `root_or_pattern_as_factual_proof`
- `derivative_as_proof`
- `irab_as_factual_certainty`
- `emphasis_as_evidence`
- `metaphor_as_literal_certificate`
- `memory_as_external_evidence`
- `model_output_as_evidence`
- `tool_output_as_certificate_without_governance`
- `residual_erasure`
- `silent_level_skip`
- `certificate_without_proof_object`
- `certificate_without_governance_gate`
- `certificate_without_reverse_trace`

## Residuals that block certification
Any blocking residual blocks certification, including missing proof object, failed governance gate, incomplete reverse trace, missing raw text anchor, silent-level-skip marker, and explicit forbidden transition markers.

## Out of scope for Phase 0
- New theoretical layers
- Redefinition of Φ/Ω semantics
- Relaxing certificate governance gates
- Expanding conceptual scope beyond contract closure

## Phase 0 closure conditions
Phase 0 is closed only when all of the following are true:
1. Φ executable tri-state contract exists and is tested.
2. Ω reverse trace is required and anchored to canonical `raw_text_units` for certificate paths.
3. Certificate gates enforce proof object, governance pass, reverse trace completeness, and residual blocking.
4. Forbidden transitions and silent-level-skip paths are blocked.
5. Regression tests lock these invariants.
6. Industrial Phase 1 roadmap is documented as hardening (not theory expansion).

## Invariant (contract freeze)
No Certificate without:
- allowed Φ path,
- complete Ω reverse trace to `raw_text_units`,
- ProofObject,
- GovernanceGate pass,
- no blocking residuals,
- no silent level skip,
- no forbidden transition marker.
