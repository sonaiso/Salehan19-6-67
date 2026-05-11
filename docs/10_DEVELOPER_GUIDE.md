# Developer Guide

## Setup

```bash
python -m pip install -e .
python -m pip install pytest
```

## Core Test Commands

```bash
python tests/verify_bayani_repository.py
PYTHONPATH=src:. python -m pytest -q
python -m pytest tests/test_coding_pr_audit.py -v
python -m pytest tests/test_coding_checks_governance.py -v
python -m pytest tests/test_coding_real_pr_fixtures.py -v
```

## CLI Examples

```bash
mcd --help
python -m mcd.cli --help
```

## Where to Add New Modules

- Runtime modules: `src/mcd/`
- Tests: `tests/`
- Governance docs/spec: `docs/`, `spec/`, `schema/`

## How to Add Examples

- Add governed examples under existing example/test fixtures in `tests/`.
- Keep traces explicit: claim -> evidence -> governance -> judgment.

## How to Add a Governed PR Fixture

1. Add fixture input artifacts (issue/patch/check context) in the existing coding auditor fixture structure.
2. Add expected governed output with reverse trace and residual handling.
3. Add/extend tests in coding auditor test modules.
4. Ensure outputs do not permit silent CERTIFICATE escalation.

## How to Avoid Violating AFJG Rules

- Never treat model output as evidence.
- Never issue CERTIFICATE without ProofObject + GovernanceGate + ReverseTrace.
- Preserve residuals; do not erase unresolved uncertainty.
- Block forbidden transitions explicitly.
