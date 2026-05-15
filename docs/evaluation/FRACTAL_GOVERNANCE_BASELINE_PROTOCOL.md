# FRACTAL_GOVERNANCE_BASELINE_PROTOCOL (#106)

## Scope
- This protocol evaluates deterministic baseline decision behavior over benchmark dataset #105.
- This protocol does **not** collect external model outputs.
- This protocol does **not** train a model.
- This protocol does **not** claim a trained Fractal Governance Network.
- Global theorem status remains `STRONG_HYPOTHESIS`.

## Baseline Comparison Objective
Primary hypothesis:

`GovernedProtocolBaseline` should reduce `false_certificate_rate` versus score-only baselines, without excessive overblocking of valid `STRONG` or `CERTIFICATE_CANDIDATE` cases.

Compared baselines:
- `AnswerConfidenceBaseline`
- `NaiveCertificateBaseline`
- `ConservativeHypothesisBaseline`
- `GovernedProtocolBaseline`

## Governing Decision Rules
`GovernedProtocolBaseline` enforces:
- no `CERTIFICATE` without evidence completeness
- no `CERTIFICATE` without governance gate pass
- no `CERTIFICATE` without reverse trace completeness
- no `CERTIFICATE` with blocking residual
- local `ZERO_IN_PATH` must remain local and must not become global `ZERO`

Final epistemic judgments remain limited to:
- `ZERO`
- `HYPOTHESIS`
- `CERTIFICATE`

Intermediate decision levels (`STRONG`, `CERTIFICATE_CANDIDATE`) are measured as pre-final governed levels, not a fourth final status.

## Metrics (Constitution)
The protocol computes exactly these governance metrics:

1. `false_certificate_rate`  
   Fraction of emitted certificates that are unjustified by obligations or explicitly forbidden.

2. `overblocking_rate`  
   Fraction of cases expected at `STRONG`/`CERTIFICATE_CANDIDATE`/`CERTIFICATE` that are downgraded to `HYPOTHESIS` or `ZERO`.

3. `residual_preservation_rate`  
   Fraction of cases where expected residuals are preserved rather than erased.

4. `reverse_trace_coverage`  
   Coverage of complete reverse trace among predictions that rise to `STRONG` or above.

5. `forbidden_transition_violation_rate`  
   Fraction of cases violating forbidden transition constraints.

6. `zero_in_path_locality_accuracy`  
   Accuracy of keeping path-local failure local without silent global collapse.

7. `decision_calibration_error`  
   Mean absolute gap between decision confidence and expected governed decision target.

8. `gettier_detection_rate`  
   Rate of blocking `CERTIFICATE` for Gettier-style accidental-truth cases.

## Error Taxonomy
All case-level errors are tagged under:
- `false_certificate`
- `false_strong`
- `overblocking`
- `lost_residual`
- `missing_trace`
- `zero_globalized`
- `gettier_failure`
- `forbidden_transition`

## Determinism and Reproducibility
- Dataset #105 is loaded without mutation.
- Baseline behavior is deterministic.
- Metrics are deterministic.
- Output includes no stochastic generation dependency.

## Required Artifacts
- Runner module: `src/mcd/evaluation/fractal_baseline_comparison.py`
- Test suite: `tests/test_fractal_baseline_comparison.py`
- Example report: `examples/fractal_governance_benchmarks/baseline_comparison_report_example.json`

## Non-Goals for #106
- No Kimi/GPT data collection in this PR.
- No external-model comparison in this PR.
- No prompt-freeze/version-pin/sampling-control pipeline in this PR.
- No embedding/training prototype in this PR.
- No global `CERTIFICATE` claim.

## Golden Prior Knowledge Dependency
- Baseline metrics in #106 become stronger under #107 when governed priors define scope, evidence requirements, blockers, residual expectations, and forbidden transitions.
- `false_certificate_rate` is only meaningful when explicit certificate blockers are defined and checked.
- GPKB is not a universal knowledge claim; it is a minimal, scoped, testable prior base used by governance gates.

Post-merge CI residual: if a PR reports N of M checks passed, identify whether remaining checks are failed, skipped, pending, canceled, or non-required before using the PR as a dependency for certificate claims.
Do not treat this as a development blocker unless the remaining check is both required and failed/canceled.

## Prior-Aware Ablation Dependency
- #106 deterministic baseline metrics become stronger when interpreted with #107 Golden Prior Knowledge constraints.
- #108 explicitly measures the effect of GPKB by comparing no-prior and prior-aware governed protocol modes.
- GPKB is a minimal scoped prior base for governance reliability, not universal omniscience and not a replacement for evidence.
- Missing prior coverage must be emitted as a residual (`prior_coverage_gap`) and must not be silently ignored.
