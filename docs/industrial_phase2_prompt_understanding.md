# Industrial Phase 2: Governed Prompt Understanding

This layer introduces a minimal **general Arabic prompt understanding** contract before answer generation.

It is **not** a fiqh/usul-only engine.  
Usul inference remains optional and is activated only when task/domain context explicitly requests it.

## Core transition

input → gates → evidence → residuals → rank → licensed output

## Payload scope

`PromptUnderstandingPayload` captures:

- prompt_understanding_schema_version
- prompt_understanding_contract_version
- raw_prompt
- normalized_prompt
- language
- vocalization_status
- segmentation_trace
- linguistic_units
- semantic_nodes
- nisbah_graph
- ifadah_units
- discourse_force
- inferred_intent
- task_type
- domain
- constraints
- activated_modules
- answer_plan
- understanding_rank (`zero | hypothesis | certificate`)
- residuals
- reverse_trace anchors to raw prompt spans

## Governance gates for certificate understanding

Certificate is blocked unless all hold:

1. `raw_prompt` exists
2. `normalized_prompt` exists
3. trace anchors exist to raw prompt spans
4. `inferred_intent` exists
5. `task_type` exists
6. no blocking residuals remain
7. schema version is supported

Missing requirements downgrade to `hypothesis` or `zero` with residuals.

## Residual governance

Prompt-understanding residual family includes:

- `missing_prompt_understanding_schema_version`
- `unsupported_prompt_understanding_schema_version`
- `prompt_missing_raw_text`
- `prompt_missing_trace_anchors`
- `prompt_intent_ambiguous`
- `prompt_task_type_missing`
- `prompt_domain_ambiguous`
- `prompt_understanding_payload_invalid`

All are non-erasing and preserved through enforcement/serialization.

