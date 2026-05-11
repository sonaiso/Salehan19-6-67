# Merge Governance

## Core Separation

```text
MERGED != CERTIFICATE
3/4 checks != CERTIFICATE
```

## Policy

- Pending checks force HYPOTHESIS.
- All checks green are necessary but not sufficient for CERTIFICATE.
- CERTIFICATE additionally requires ProofObject, GovernanceGate, and ReverseTrace.
- Branch protection is required at GitHub governance level (outside source code).

## Why This Matters

PR #57, PR #58, and PR #59 demonstrate that repository merge state and epistemic certification are different governance levels.

Operational consequence:

- Merge can complete while epistemic certainty remains unresolved.
- Certification must remain blocked until governance requirements are fully satisfied.
