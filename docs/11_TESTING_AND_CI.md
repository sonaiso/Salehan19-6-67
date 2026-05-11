# Testing and CI

## Repository Verification

```bash
python tests/verify_bayani_repository.py
```

## Coding Copilot Tests

```bash
python -m pytest tests/test_coding_pr_audit.py -v
python -m pytest tests/test_coding_checks_governance.py -v
python -m pytest tests/test_coding_real_pr_fixtures.py -v
```

## Bayani Verifier and Full Suite

```bash
PYTHONPATH=src:. python -m pytest -q
```

## Expected No-Network Principle

Test execution should remain deterministic and local; verification must not depend on live network evidence during CI runs.

## Pending Checks Policy

Pending or missing required checks force HYPOTHESIS in governed PR judgment and cannot be promoted to CERTIFICATE.

## What Counts as Evidence

- reproducible test outputs
- auditable static artifacts
- traceable governance decisions
- complete reverse trace linked to claim type

## What Does Not Count as Evidence

- model text alone
- rhetorical emphasis
- merged state alone
- partial check success (for example 3/4 checks)
- linguistic structure without governed proof linkage
