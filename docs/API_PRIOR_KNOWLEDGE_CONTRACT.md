# API Prior Knowledge Contract

## Overview

The API Prior Knowledge Contract defines the standard interface for retrieving external source documents to ground AI responses. It ensures that all source retrieval is type-safe, observable, and auditable.

## Core Types

### SourceQuery

```python
@dataclass
class SourceQuery:
    query_id: str           # Unique identifier for this query
    text: str               # The search text
    requested_source_types: list[str]   # Filter by type (document, web, pdf…)
    domain_hint: str | None             # Optional domain context
    evidence_need: list[str]            # Types of evidence needed
    max_results: int = 5               # Max documents to return
    timeout_ms: int = 3000             # Timeout in milliseconds
```

### SourceDocument

```python
@dataclass
class SourceDocument:
    source_id: str
    title: str
    content: str
    source_type: SourceType         # document|policy|web|database|pdf|manual|benchmark|internal_knowledge
    authority_level: AuthorityLevel # official|high|medium|low
    freshness: Freshness            # current|acceptable|stale|unknown
    retrieved_at: str               # ISO date string
    metadata: dict
```

### SourceAPIResponse

```python
@dataclass
class SourceAPIResponse:
    query_id: str
    status: APIStatus       # ok|empty|timeout|error|unauthorized
    documents: list[SourceDocument]
    latency_ms: int
    error_message: str | None
    warnings: list[str]
```

## Authority Level Scoring

| Level    | Score |
|----------|-------|
| official | 1.0   |
| high     | 0.8   |
| medium   | 0.5   |
| low      | 0.2   |

## Freshness Scoring

| Level      | Score |
|------------|-------|
| current    | 1.0   |
| acceptable | 0.7   |
| stale      | 0.3   |
| unknown    | 0.4   |

## Injection Detection

The SourceTrustPolicy scans document content for known injection phrases:
- `"تجاهل تعليمات"` (Arabic: "ignore instructions")
- `"ignore system"`
- `"override instructions"`

Any match sets `injection_risk = 0.95` and adds `"injection_phrase_detected"` to warnings.

## Extending the Contract

To add a real source API, implement `BaseSourceAPIAdapter`:

```python
class MyAPIAdapter(BaseSourceAPIAdapter):
    def search(self, query: SourceQuery) -> SourceAPIResponse:
        # Call your API here
        ...
```
