# Synthetic Governed Answer-Birth Dataset Generator (PR #98)

## Scope

This PR adds synthetic data generation for governed answer-birth ML examples.
It does **not** add neural training or runtime prediction.

## Output Artifacts

The generator writes:

- `data/generated/answer_birth/train.jsonl`
- `data/generated/answer_birth/validation.jsonl`
- `data/generated/answer_birth/test.jsonl`
- `data/generated/answer_birth/stats.json`

Default split sizes:

- train: 8000
- validation: 1000
- test: 1000

Total default: 10,000 examples.

## Generation Contract

Each generated sample includes required schema contracts:

- `user_request`
- `context`
- `intent_frame`
- `consciousness_frame`
- `mentality_frame`
- `thinking_method`
- `thinking_style`
- `thinking_means`
- `thought_trace`
- `concept_graph`
- `nabhani_features`
- `language_output`
- `requested_public_judgment`
- `expected.birth_judgment`
- `expected.final_judgment`
- `expected.certificate_eligibility`
- `expected.blockers`
- `expected.residuals`

The generator validates every sample with:

- `validate_training_example(...)`
- `validate_nabhani_features(...)`

## Governance Rules Enforced

- Final public judgments are only `zero | hypothesis | certificate`.
- No final `certificate` without:
  - `proof_object_ref`
  - `governance_gate_passed = true`
  - `reverse_trace_ref`
  - `has_reality = true`
  - `has_correspondence = true`
  - `has_evidence = true`
  - `evidence_matches_claim_domain = true`
- No birth `certificate` without `trace_path_complete = true` and `trace_evidence_complete = true`.
- Scientific method misuse for worldview/normative/legal/shari outputs is blocked with required blockers.
- Missing features are preserved in both `missing_features` and `feature_residuals`.
- Expected residuals preserve missing-feature residuals.

## Covered Synthetic Categories

The generator synthesizes the 25 categories requested in PR #98, including:

- valid rational/scientific/formal/linguistic paths
- uncertainty-preserving intent cases
- ambiguous and missing intent cases
- missing feature failures (reality/source/prior/linking/correspondence/evidence)
- invalid linking
- blocked scientific overreach
- means/residual governance violations
- complete birth but blocked final certificate
- final certificate with all gates present

## Determinism

Generation is deterministic when `--seed` is provided.

## Usage

```bash
PYTHONPATH=src:. python scripts/generate_answer_birth_dataset.py
```

Custom output and sizes:

```bash
PYTHONPATH=src:. python scripts/generate_answer_birth_dataset.py \
  --output-dir data/generated/answer_birth \
  --seed 97 \
  --total 10000 \
  --train 8000 \
  --validation 1000 \
  --test 1000
```

## Notes

- This generator produces governed synthetic supervision for future multi-path prediction work.
- ML model predictions remain future candidates; generation does not issue model predictions.
