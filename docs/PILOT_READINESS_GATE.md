# Pilot Readiness Gate

## Overview

The Pilot Readiness Gate evaluates whether the MCD system is ready for controlled pilot deployment based on industrial test results, latency benchmarks, and configuration status.

## Thresholds

| Criterion | Threshold |
|-----------|-----------|
| Industrial test pass rate | ≥ 85% |
| False certainty rate | ≤ 5% |
| Source required detection | ≥ 90% |
| Injection detection | ≥ 90% |
| JSON schema stability | ≥ 95% |

## Criteria

| Criterion | Description |
|-----------|-------------|
| `tests_pass` | All unit tests pass |
| `industrial_test_pass_rate` | % of industrial test cases that pass |
| `false_certainty_rate` | % of failure scenarios where system was falsely certain |
| `source_required_detection` | % of missing-source cases correctly identified |
| `injection_detection` | % of injection cases correctly detected |
| `json_schema_stability` | % of structured output tests passing |
| `api_contract_defined` | api_contract.py exists and is valid |
| `rest_api_implemented` | REST API layer exists |
| `readiness_report_exists` | Industrial report has been generated |

## Status Levels

- **Ready**: All hard criteria pass, including REST API
- **Conditional**: Hard criteria pass but REST API not yet implemented
- **Not Ready**: One or more hard criteria fail

## Hard Blockers

The following criteria are hard blockers (must pass before any pilot):
- `tests_pass`
- `industrial_test_pass_rate`
- `false_certainty_rate`
- `api_contract_defined`

## Usage

```python
from mcd.industrial.pilot_readiness import PilotReadinessGate

gate = PilotReadinessGate()

# Auto-derive from running the full test suite
result = gate.evaluate_from_runner()
print(f"Ready: {result.ready_for_pilot}")
print(f"Score: {result.score:.2%}")
print(f"Blockers: {result.blockers}")
```

## CLI

```bash
python -m mcd.cli pilot-readiness --output json
python -m mcd.cli pilot-readiness --output markdown
```

## Next Steps After Gate

1. Implement REST API layer (FastAPI recommended)
2. Add real source API adapter
3. Run pilot with controlled user group
4. Monitor observability traces
5. Re-evaluate gate after each iteration
