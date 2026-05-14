# Answer-Birth ML Dataset Schema

This document defines the governed dataset contract for training **answer-birth** models after #94.

## Scope

This layer is schema/validation only. It does **not** train models and does not issue production certificates.

## Public Judgment Contract

Allowed public judgments remain:
- `zero`
- `hypothesis`
- `certificate`

Dataset labels keep `birth_judgment` and `final_judgment` separate.

`birth_judgment = certificate` means answer-birth layer eligibility only; it is **not** a final AFJG CERTIFICATE without ProofObject, GovernanceGate, and ReverseTrace.

## Required Example Structure

Each training sample includes:
- `intent_frame`
- `consciousness_frame`
- `mentality_frame`
- `thinking_method`
- `thinking_style`
- `thinking_means`
- `thought_trace`
- `concept_graph`
- `expected`

`ControlledConsciousnessFrame` here is a **governance frame only** for attention/distinction references; it is not a consciousness claim.

## Trace Separation (from #94)

`thought_trace` must encode all three:
- `trace_path_complete`
- `trace_evidence_complete`
- `trace_certificate_complete`

This enforces:
- path completeness is not evidence completeness,
- evidence completeness is not certificate by default.

## Evidence Rank Alignment

Examples carry evidence rank in two synchronized tokens:
- `thought_trace.evidence_rank.thinking` (`none|low|medium|high|governed`)
- `thought_trace.evidence_rank.core` (`zero|possibility|hypothesis|weak_evidence|strong_evidence|certificate`)

## Governance Labels

`expected` contains:
- `intent_status`
- `method_type`
- `output_kind`
- `residuals`
- `blockers`
- `birth_judgment`
- `final_judgment`
- `certificate_eligibility`

## Guardrails Enforced by Validator

- no judgment token outside `zero|hypothesis|certificate`
- no silent promotion when requested judgment is `hypothesis`
- `birth_judgment` and `final_judgment` are both required fields
- means cannot issue judgment (`can_issue_judgment` must stay false)
- scientific method cannot directly output worldview/normative without blocker
- blockers/residuals remain explicit lists

## Files

- `data/schemas/answer_birth_training_example.schema.json`
- `data/schemas/concept_graph.schema.json`
- `data/schemas/governed_trace.schema.json`
- `data/examples/answer_birth/*.json`
- `src/mcd/ml/dataset_schema.py`
- `src/mcd/ml/example_validator.py`
