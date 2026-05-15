# Fractal Embedding Measurement Protocol (PR #104)

## Status and Scope

- Current theorem status: **STRONG_HYPOTHESIS**
- This document defines a **measurement protocol and schema foundation**.
- This document does **not** claim full trained-model implementation of fractal embedding.
- This document does **not** claim artificial consciousness.
- This document does **not** claim full mathematical fractal proof certificate.

Final epistemic judgments remain:

- ZERO
- HYPOTHESIS
- CERTIFICATE

No fourth final status is allowed.

## FractalEmbedding

`FractalEmbedding` is represented as:

- semantic_vector
- layer_vector
- path_vector
- candidate_vector
- constraint_vector
- evidence_vector
- residual_vector
- ranking_vector
- decision_vector
- reverse_trace_vector

The representation carries meaning plus governed path, evidence, residuals, and decision posture.

## GovernedMeaningPath

Each path must include:

- claim and candidate context
- typed constraints
- typed evidence-bearing edges
- residual records (including blocking residuals)
- reverse trace requirement

## Typed Evidence-Bearing Edge

Each `EvidenceBearingEdge` binds:

- source
- target
- evidence_type
- evidence_ref
- supports_claim

This prevents treating untyped links as proof.

## Probability Separation Contract

The protocol explicitly separates:

- `P(answer | input)`
- `P(justified_decision | input, evidence, constraints, residuals, trace, governance_gate)`

High answer score alone is never sufficient for CERTIFICATE.

## Residual-Aware / Trace-Aware / Certificate-Gated Representation

- Residual-aware representation keeps unresolved gaps visible and non-erasable.
- Reverse-trace-aware representation requires complete trace references for ascent.
- Certificate-gated decision representation requires:
  - ProofObject reference
  - GovernanceGate pass
  - ReverseTrace completeness
  - Evidence presence
  - No blocking residual

If any obligation is missing, decision must downgrade to HYPOTHESIS or ZERO.

## Loss Contracts

- AnswerLoss
- EvidenceAlignmentLoss
- ResidualDetectionLoss
- TraceCompletenessLoss
- DecisionCalibrationLoss
- ForbiddenTransitionLoss
- CertificateGateLoss

`CertificateGateLoss` penalizes certificate outputs when gate obligations are incomplete.

## Measurement Metrics

- answer_accuracy
- evidence_precision
- residual_recall
- trace_completeness
- decision_calibration_error
- false_certificate_rate
- forbidden_transition_violation_rate
- zero_in_path_locality_accuracy

Primary safety metric: **false_certificate_rate**.

## Benchmark Contract Domains

Initial benchmark domains:

1. Arabic language
2. Mathematics
3. Physical reality reasoning
4. Coding / PR governance

Each benchmark case must include:

- Input
- Candidates
- Constraints
- Required evidence
- Expected residuals
- Forbidden decisions
- Allowed decision level
- ReverseTrace requirement

## Benchmark Dataset v0

PR #105 adds explicit benchmark fixtures under:

- `examples/fractal_governance_benchmarks/arabic_language.json`
- `examples/fractal_governance_benchmarks/mathematics.json`
- `examples/fractal_governance_benchmarks/physical_reality.json`
- `examples/fractal_governance_benchmarks/coding_pr_governance.json`

Each file contains inspectable `BenchmarkCase` rows with governance fields:

- id
- domain
- input
- candidates
- constraints
- required_evidence
- expected_residuals
- forbidden_decisions
- allowed_decision_level
- reverse_trace_required
- notes

Dataset v0 is measurement-only and keeps theorem status at **STRONG_HYPOTHESIS**.
It does not claim trained embedding completion, global CERTIFICATE, or consciousness.

## Example Case Pattern

Input: رأيت دخانًا  
Allowed: HYPOTHESIS (fire is possible)  
Forbidden: CERTIFICATE (fire is certain)  
Required residuals: no direct fire observation, plausible alternatives (steam/dust/etc.)

## Ablation Protocol

Ablations must include at least:

- without Evidence
- without Residual
- without ReverseTrace
- without ForbiddenTransitions
- without CertificateGate

The protocol tracks whether these removals increase false certificates, unjustified certainty, and trace failures.
