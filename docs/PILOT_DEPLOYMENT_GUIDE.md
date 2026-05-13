# Pilot Deployment Guide (Controlled Scope)

This guide defines reproducible pilot deployment and validation steps.

## Scope

- Allowed: controlled scientific-industrial pilot
- Not allowed: production certification claims

## Preconditions

1. Python 3.11+ available
2. Test dependencies installed
3. Working tree at target pilot revision

## Setup

```bash
python -m pip install -e ".[test]"
```

## Baseline Validation

```bash
PYTHONPATH=src:. python -m pytest -q
```

## Pilot Validation Artifact Generation

```bash
python scripts/run_pilot_validation.py --output artifacts/pilot/pilot_validation_report.json
```

## Optional CLI Demonstrations

```bash
bash examples/pilot/demo_cli_validation.sh
```

## Optional API Demonstration

```bash
bash examples/pilot/demo_api_validation.sh
```

## Replay Reconstruction Check

Use `artifacts/pilot/pilot_validation_report.json` and verify:

- `replay_integrity_contract.valid_event_log == true`
- `replay_integrity_contract.judgment_consistent == true`
- `replay_integrity_contract.contract_holds == true`

## Acceptance for Pilot

Pilot acceptance requires:

- baseline tests pass
- pilot validation report generated
- report final status remains `HYPOTHESIS` (pilot posture)
- no claim of production certification in release messaging

