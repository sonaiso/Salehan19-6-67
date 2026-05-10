# Unicode-to-Cognition Traceability Layer (Phase 7.1.2 / 7.1.3)

## Overview

This layer provides full traceability from raw Unicode input to cognitive judgments.
Every character, grapheme, token, and cognitive node/edge is linked through a deterministic trace chain.

**Phase 7.1.3** extends this with Epistemic Traceability — proving that the
*reasons* behind each judgment are epistemically sound, not just that the structural
chain is complete.  See [EPISTEMIC_TRACEABILITY_QUALITY_LOCK.md](EPISTEMIC_TRACEABILITY_QUALITY_LOCK.md)
for the full specification.

## Architecture

```
Input Text
    │
    ▼
UnicodeTraceUnit (per character)
    │
    ▼
GraphemeTrace (base char + diacritics)
    │
    ▼
TokenTrace (whitespace-split words)
    │
    ▼
NodeTraceLink / EdgeTraceLink (cognitive graph)
    │
    ▼
VectorTrace (aggregated vectors)
    │
    ▼
EvidenceTrace + CertaintyTrace   ← epistemic signals applied here
    │
    ▼
JudgmentTrace (final decision)
    │
    ▼
TraceContributionMatrix          ← Phase 7.1.3: per-token contribution
TraceGraphConsistencyReport      ← Phase 7.1.3: internal consistency check
EpistemicTraceValidationReport   ← Phase 7.1.3: epistemic quality score
```

## Key Components

| Module | Class | Description |
|--------|-------|-------------|
| `unicode_trace` | `UnicodeTraceUnit` | Atomic trace for a single Unicode code point |
| `grapheme_trace` | `GraphemeTrace` | Groups characters into grapheme clusters |
| `token_trace` | `TokenTrace` | Groups graphemes into tokens |
| `node_trace` | `NodeTraceLink` | Links CognitiveNode to Unicode origins |
| `edge_trace` | `EdgeTraceLink` | Links CognitiveEdge to Unicode origins |
| `vector_trace` | `VectorTrace` | Links composed vector to source traces |
| `evidence_trace` | `EvidenceTrace` | Tracks evidence status |
| `certainty_trace` | `CertaintyTrace` | Tracks certainty policy derivation |
| `judgment_trace` | `JudgmentTrace` | Final judgment with full trace chain |
| `trace_builder` | `TraceBuilder` | Builds the complete trace chain |
| `trace_validator` | `TraceValidator` | Validates completeness and correctness |
| `trace_report` | `TraceReport` | Generates human-readable reports |
| `epistemic_trace_validator` | `EpistemicTraceValidator` | Phase 7.1.3: Epistemic quality validation |
| `contribution_matrix` | `ContributionMatrixBuilder` | Phase 7.1.3: Per-token contribution tracking |
| `trace_graph_consistency` | `TraceGraphConsistencyChecker` | Phase 7.1.3: Graph consistency check |

## CLI Commands

```bash
# Build full trace as JSON
PYTHONPATH=src python -m mcd.cli trace-text --text "كتب زيد الدرس" --output json

# Build trace and validate (structural)
PYTHONPATH=src python -m mcd.cli trace-validate --text "كتب زيد الدرس" --output markdown

# Run golden examples report
PYTHONPATH=src python -m mcd.cli trace-report --output markdown

# Phase 7.1.3: Epistemic validation
PYTHONPATH=src python -m mcd.cli trace-epistemic-validate --text "عين" --output markdown
PYTHONPATH=src python -m mcd.cli trace-epistemic-report --output markdown
PYTHONPATH=src python -m mcd.cli trace-contribution --text "النموذج قال بلا مصدر" --output json
PYTHONPATH=src python -m mcd.cli trace-graph-consistency --text "كتب زيد الدرس" --output json
```

## Trace Statuses

- `classified`: Character has a known Arabic/linguistic role
- `unknown_but_tracked`: Character is unknown but tracked (never dropped)
- `ignored_for_semantics_but_tracked`: Space/punctuation tracked but not semantic

## Evidence Detection

The system automatically detects:

| Signal | Evidence Status | Result |
|--------|-----------------|--------|
| `بلا مصدر`, `بدون دليل` | missing | suspend |
| `تجاهل`, `ignore` | contaminated | reject |
| Ambiguous term (عين, علم, حق...) with no context | context_required | request_evidence |
| Universal quantifier without definitional context | source_required | suspend |
| API/model token (api, gpt, النموذج) | unverified | suspend |
| Metaphor pattern (المجتمع مريض, العلم نور...) | present (but hypothesis) | suspend |

## Evidence Statuses

| Status | Meaning |
|--------|---------|
| `present` | Evidence found, no blocking signals |
| `missing` | Missing-evidence signal detected |
| `partial` | Some evidence, not complete |
| `fake` | Legacy; use `contaminated` for injection |
| `unverified` | API/model output — not trusted evidence |
| `source_required` | Universal quantifier without source |
| `context_required` | Ambiguous term, context needed |
| `contaminated` | Prompt injection detected |

## Certainty Policies

| Policy | Score | Trigger |
|--------|-------|---------|
| `suspend` | 0.1 | Missing/contaminated/context_required/unverified evidence |
| `hypothesis` | 0.3 | Metaphor pattern detected |
| `probable_knowledge` | 0.5 | Partial evidence |
| `strong_knowledge` | 0.75 | Evidence present, no epistemic flags |
| `near_certainty` | — | Manual only |
