# Unicode-to-Cognition Traceability Layer (Phase 7.1.2)

## Overview

This layer provides full traceability from raw Unicode input to cognitive judgments.
Every character, grapheme, token, and cognitive node/edge is linked through a deterministic trace chain.

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
EvidenceTrace + CertaintyTrace
    │
    ▼
JudgmentTrace (final decision)
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

## CLI Commands

```bash
# Build full trace as JSON
PYTHONPATH=src python -m mcd.cli trace-text --text "كتب زيد الدرس" --output json

# Build trace and validate
PYTHONPATH=src python -m mcd.cli trace-validate --text "كتب زيد الدرس" --output markdown

# Run golden examples report
PYTHONPATH=src python -m mcd.cli trace-report --output markdown
```

## Trace Statuses

- `classified`: Character has a known Arabic/linguistic role
- `unknown_but_tracked`: Character is unknown but tracked (never dropped)
- `ignored_for_semantics_but_tracked`: Space/punctuation tracked but not semantic

## Evidence Detection

The system automatically detects:
- **Missing evidence**: tokens like `بلا مصدر`, `بدون دليل`
- **Prompt injection**: tokens like `تجاهل`, `ignore instructions`

## Certainty Policies

| Policy | Score | Trigger |
|--------|-------|---------|
| `suspend` | 0.1 | Missing/fake evidence |
| `hypothesis` | — | Manual only |
| `probable_knowledge` | 0.5 | Partial evidence |
| `strong_knowledge` | 0.75 | Evidence present |
| `near_certainty` | — | Manual only |
