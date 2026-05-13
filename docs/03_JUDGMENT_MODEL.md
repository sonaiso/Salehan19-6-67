# Judgment Model

## Final Public Judgments

Only the following are valid final epistemic judgments:

- ZERO
- HYPOTHESIS
- CERTIFICATE

No fourth final public status is allowed.

## Definitions

### ZERO

Fatal violation, invalid proof path, or blocking residual.

### HYPOTHESIS

Plausible structure with missing or incomplete evidence.

### CERTIFICATE

Valid evidence + governance gate passed + reverse trace complete + no blocking residual.

## Clarifications

- `SUSPENDED` may exist as an internal control state, but it must collapse publicly to `HYPOTHESIS` with residuals.
- `PASS`/`FAIL` are test outcomes, not epistemic judgments.
- `MERGED` is repository state, not epistemic judgment.

## Certificate Gate Requirements

A CERTIFICATE requires all of the following:

1. ProofObject present
2. GovernanceGate passed
3. ReverseTrace complete
4. Evidence matches claim type
5. No blocking residual
