# Industrial Phase 3A+ — Fractal Operator Composition Contract

## Scope
Phase 3A established local governed operators (single typed transitions).
Phase 3A+ governs how those valid local operators are composed.
This phase does **not** implement the full quantitative reasoning engine.

## Phase 3A recap (local contracts)
Each local operator remains governed as:

`input -> gates -> evidence -> residuals -> rank -> licensed output`

Local contract validation still enforces:
- no free-rule learning
- no multi-transition shortcut in one operator
- no forbidden local final output
- no certificate-capable local operator without reverse trace requirement

## Phase 3A+ addition (composition contracts)
Composition introduces governed chain validation so valid local operators cannot form an invalid global jump.

Composition contract fields:
- chain_id
- operators[]
- layer_sequence[]
- input_type
- output_type
- rank_policy
- residual_policy
- forbidden_final_outputs
- required_trace_composition

## Composition rules
For a chain to be admitted:
1. Every operator is already valid under `OperatorContract`.
2. For each adjacent pair:
   - `previous.layer_to == next.layer_from`
   - `previous.output_type == next.input_type`
3. Chain `output_type` must equal final operator `output_type`.
4. Forbidden final outputs (`Judgment`, `Certificate`, `FinalAnswer`, `ProjectConclusion`) are blocked unless the final layer is explicitly licensed.
5. Chain rank is weak-link bounded: it cannot exceed the weakest operator rank.
6. Chain residuals are non-erasing union of operator residual policies and emitted chain residuals.
7. Chain trace composes local traces into one reverse trace.
8. Missing trace composition blocks certificate-capable chains.
9. Multi-transition shortcuts remain forbidden unless represented as explicit operator sequences.

## Residual taxonomy additions
- `operator_chain_type_mismatch`
- `operator_chain_layer_mismatch`
- `operator_chain_forbidden_final_output`
- `operator_chain_missing_trace_composition`
- `operator_chain_rank_overclaim`
- `operator_chain_residual_erasure`
- `operator_chain_invalid`

## Phase 3B handoff
Phase 3B will implement the quantitative operator chain itself (engine-level reasoning), e.g.:

`QuantityExtraction -> UnitNormalization -> RoleBinding -> LawSelection -> ConstraintEvaluation -> QuantitativeProofObject`

Phase 3A+ only guarantees composition governance before that engine work begins.
