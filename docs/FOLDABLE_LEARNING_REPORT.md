# Foldable Cognitive Residual Learning — CI Check Report

## Phase 7.2 Status: ✅ PASS

Generated automatically from `mcd.cli fold-memory-report --output markdown`.

## Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Fold Consistency Score | 1.0000 | ≥ 0.95 | ✅ PASS |
| Residual Coverage Score | 1.0000 | ≥ 0.90 | ✅ PASS |
| Recall Precision Estimate | 0.8700 | ≥ 0.85 | ✅ PASS |
| Pattern Reuse Rate | 0.8800 | ≥ 0.50 | ✅ PASS |

## Pipeline Summary

| Component | Count |
|-----------|-------|
| Mock GPT Proposals | 100 |
| Cognitive Residuals Generated | 100 |
| Blocking Residuals | 17 |
| Fold Signatures Created | 100 |
| Learning Actions Generated | 297 |
| Proposed Invariants | 11 |

## Residuals by Type

| Residual Type | Count |
|---------------|-------|
| evidence_residual | 88 |
| certainty_residual | 32 |
| tool_evidence_residual | 13 |
| ambiguity_residual | 13 |
| gpt_as_evidence_residual | 7 |
| metaphor_residual | 6 |
| causality_residual | 6 |
| injection_residual | 6 |
| traceability_residual | 6 |
| unsupported_generalization_residual | 6 |
| harm_haram_residual | 5 |
| analogy_residual | 5 |
| domain_residual | 5 |

## Key Guarantees

- **GPT output is NEVER evidence** — `gpt_as_evidence_residual` triggers `reject_proposal` + `require_human_review`
- **No real API calls** — all computation is pure in-memory Python
- **No GraphRAG** — forbidden by spec
- **All 15 fold families** registered in `FoldSignatureRegistry`
- **Invariant threshold** = 3 occurrences (per `MathematicalPatternMiner`)

## CLI Commands

```bash
# Full pipeline
PYTHONPATH=src python -m mcd.cli fold-residuals --output json

# Memory report with metrics
PYTHONPATH=src python -m mcd.cli fold-memory-report --output markdown

# Recall engine
PYTHONPATH=src python -m mcd.cli fold-recall --text "هذا صحيح"

# Fold-unfold consistency
PYTHONPATH=src python -m mcd.cli fold-consistency --output json

# Pattern mining
PYTHONPATH=src python -m mcd.cli pattern-mine --output json
```

## Test Suite

All 1873 tests pass including 9 new foldable learning test files (60+ tests).
