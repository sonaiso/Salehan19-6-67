# Industrial Phase 3 — Fractal Governed Operator Learning

## Scope
This phase establishes governance foundations only.
It does **not** implement a broad quantitative reasoning engine.

## Core rule
Learning must not produce free rules.
Learning must produce typed transition-repair operators for exactly one transition `Lᵢ -> Lᵢ₊₁`.

## Forbidden learning pattern
Rules like `solve_airport_problem` are forbidden because they bypass typed transition governance.

## Operator contract shape
Every learned operator is governed as:

`input -> gates -> evidence -> residuals -> rank -> licensed output`

Required declarations:
- layer_from
- layer_to
- input_type
- output_type
- missing_gate
- gates
- evidence requirements
- residual policy
- rank (`zero | hypothesis | certificate`)
- forbidden_outputs
- reverse_trace requirements

## Governance requirements
- No certificate without `ProofObject`.
- No certificate without `GovernanceGate`.
- No certificate without `ReverseTrace`.
- No learning update without residual accounting.

## Locality rule
A local operator cannot emit final judgment/certificate/answer/project conclusion unless that output type belongs to that final layer.

## Registry policy
Fractal registry accepts only validated operators and rejects:
- free rules
- multi-transition operators
- operators without gates
- operators without residual policy
- operators with forbidden final outputs

## Phase-3B handoff
Quantitative reasoning chain is intentionally deferred to a separate PR as composition of local operators:

`QuantityExtraction -> UnitNormalization -> RoleBinding -> LawSelection -> ConstraintEvaluation -> GovernedJudgment`
