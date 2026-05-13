# External Audit Package (v0.1.0-pilot)

Status: **Pilot-qualified package** for controlled scientific-industrial evaluation.  
Posture: **Not production-certified** and **not theory-complete**.

## Package Scope

This package supports external audit of three qualification closures:

1. Runtime ↔ Formal equivalence baseline
2. Replay integrity contract
3. Layer sovereignty registry

## Included Artifacts

- `research/formal/runtime_formal_equivalence_truth_table.json`
- `src/mcd/qualification/runtime_formal_equivalence.py`
- `src/mcd/qualification/layer_sovereignty_registry.py`
- `src/mcd/audit/backend/persistent.py`
- `tests/test_runtime_formal_equivalence.py`
- `tests/test_replay_integrity_contract.py`
- `tests/test_layer_sovereignty_registry.py`
- `scripts/run_pilot_validation.py`
- `examples/pilot/`

## What the Project Proves

- Governed public judgment collapse is bounded to `ZERO | HYPOTHESIS | CERTIFICATE`.
- Certificate gating remains blocked without ProofObject + GovernanceGate + ReverseTrace.
- Replay integrity contract is machine-checked at runtime for valid immutable event logs.
- Layer sovereignty constraints are executable and prevent silent level skipping.

## What the Project Does Not Prove

- Full refinement proof for the entire runtime.
- Lean-complete replay theorem.
- Full Meaning Ascent Algebra formalization.
- Production hardening or enterprise deployment readiness.

## Reproducible Validation Procedure

```bash
python scripts/run_pilot_validation.py --output artifacts/pilot/pilot_validation_report.json
```

The generated report includes:

- runtime-formal equivalence summary against committed truth table,
- replay integrity reconstruction snapshot,
- layer sovereignty registry consistency checks,
- explicit `HYPOTHESIS` final package status for pilot scope.

## Replay Reconstruction Procedure

The report captures:

- `original_judgment_sequence`
- `replayed_judgment_sequence`
- `judgment_consistent`
- `contract_holds`

Contract statement:

`ValidEventLog=true => Replay(log) preserves public_judgment sequence`.

## Lean Proof Boundary

- Lean-aligned equivalence is currently enforced through truth-table obligations and runtime tests.
- This package does not claim complete Lean proof coverage of replay or full runtime semantics.

## LocalCertificate vs GlobalCertificate

- **LocalCertificate**: scoped certificate result at local evaluation path with local evidence and gate checks.
- **GlobalCertificate**: cross-layer governed certificate requiring complete chain consistency, sovereignty constraints, and no blocking residuals across the full ascent.

This pilot package supports local governed verification patterns and partial global-governance artifacts; it does not claim complete global certification closure.

## Certificate Failure Conditions

Certificate must fail or downgrade when any of the following holds:

- missing ProofObject
- GovernanceGate failed
- ReverseTrace incomplete
- forbidden transition detected
- residual erasure detected
- evidence rank below required threshold
- rank gap / missing evidence / unresolved conflict

