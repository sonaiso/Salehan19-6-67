# Unified Φ/Ω/Certificate Contract

## Φ (forward transition)

### Input
`(U, P, L, R, G, C, W, X)`

### Output
`(U', judgment, known, passed, residuals)`

### Tri-state judgment contract
- `C is None` -> `judgment=suspended`, `known=0`, `passed=0`, residual includes `transition_condition_unknown`
- `C is False` -> `judgment=blocked`, `known=1`, `passed=0`, residual includes `transition_condition_failed`
- `C is True` -> `judgment=allowed`, `known=1`, `passed=1`, `residuals=[]`

## Ω (reverse trace)

### Input
- final unit/final judgment context
- proof object reference
- reverse trace record

### Required anchor
- canonical `raw_text_units`

### Output
- `complete`: reverse path is complete and governed
- `incomplete`: reverse path is missing required anchors or blocked by governance constraints

## Certificate contract
Certificate may only exist if **all** of the following are valid:
1. Φ allows the forward transition.
2. Ω reverse trace is complete and anchored to `raw_text_units`.
3. ProofObject exists.
4. GovernanceGate passes.
5. No blocking residuals remain.
6. No silent-level-skip marker exists.
7. No forbidden transition marker exists.

## Forbidden certificate shortcuts
Certificate must be downgraded/rejected on:
- missing proof object
- missing/failed governance gate
- missing/incomplete reverse trace
- missing raw text anchor in reverse trace path
- blocking residual presence
- `silent_level_skip`
- any forbidden transition marker
