# 24 — Node / Edge / Dimension / Domain / Relation Model

## MinimalFractalNode

Required fields:

- `node_id`
- `rank`
- `node_type`
- `domain`
- `dimensions`
- `gates`
- `scores`
- `relations`
- `incoming_edges`
- `outgoing_edges`
- `residuals`
- `trace_refs`
- `allowed_next`
- `forbidden_transitions`

Rules:

- no node without `trace_refs`
- no node without at least one gate
- no node without domain or explicit `domain_missing` residual
- node alone cannot issue `CERTIFICATE`
- node score cannot override gates

## MinimalFractalEdge

Required fields:

- `edge_id`
- `source_node`
- `target_node`
- `morphism_id`
- `relation_type`
- `preserves`
- `adds`
- `forbids`
- `gate_requirements`
- `score_effects`
- `residual_policy`
- `trace_policy`

Rules:

- no edge without `morphism_id`
- no edge without `relation_type`
- edge preserves trace unless marked generated with reason
- edge cannot erase residuals silently
- edge cannot create evidence unless relation is governed evidence relation
- no silent level skip

## EpistemicDimension

Required fields:

- `dimension_id`
- `dimension_type`
- `gate`
- `score`
- `residuals`
- `trace_refs`

Dimension types:

- `existence`
- `trace`
- `distinction`
- `designation`
- `identity`
- `universal_particular`
- `domain`
- `aspect`
- `time`
- `judgment_rank`
- `relation`
- `evidence`
- `certainty`
- `residual`
- `reverse_trace`
- `governance`

Rules:

- every dimension has gate and score
- `gate ∈ {0,1}`
- `score ∈ [0,1]`
- score cannot open gate
- failed critical dimension blocks transition

## Domains

- linguistic
- morphological
- syntactic
- semantic
- rhetorical
- factual
- legal
- shari
- scientific
- mathematical
- programming
- governance
- metaphorical

## Relation Types

- matching
- inclusion
- implication
- reference
- nisbah
- cause
- condition
- purpose
- metaphor
- evidence
- judgment
- governance
- trace

Rules:

- no relation without domain
- no domain transfer without bridge
- metaphor relation cannot become literal certificate
- evidence relation requires evidence governance
- judgment relation requires evidence and trace

