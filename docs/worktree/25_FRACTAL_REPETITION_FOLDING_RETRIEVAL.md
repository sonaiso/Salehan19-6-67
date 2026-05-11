# 25 — Fractal Repetition, Folding, and Retrieval

## Fractal Repetition Rule

The same governed template is reused at every epistemic rank:

```text
Gate → Score → Dimension → Domain → Relation → Edge → Residual → Trace → Judgment Boundary
```

This avoids layer drift and blocks silent transition shortcuts.

## FoldedNodeSummary

Required fields:

- `node_id`
- `passed_gates_count`
- `failed_critical_gates`
- `completeness_score`
- `domain`
- `relation_count`
- `blocking_residuals`
- `trace_status`
- `judgment_boundary`

## RetrievalPath

Required fields:

- `folded_node_id`
- `expanded_dimensions`
- `expanded_edges`
- `residual_path`
- `reverse_trace`

## Folding / Retrieval Rules

- folding preserves all blocking residuals
- folding preserves trace status
- retrieval reconstructs dimensions and edges
- no fold may hide failed gates
- retrieval without trace remains below certificate boundary

