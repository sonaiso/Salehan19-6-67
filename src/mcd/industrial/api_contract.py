"""API Contract for prior knowledge sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SourceType = Literal["document", "policy", "web", "database", "pdf", "manual", "benchmark", "internal_knowledge"]
AuthorityLevel = Literal["low", "medium", "high", "official"]
Freshness = Literal["unknown", "stale", "acceptable", "current"]
APIStatus = Literal["ok", "empty", "timeout", "error", "unauthorized"]


@dataclass
class SourceQuery:
    query_id: str
    text: str
    requested_source_types: list[str] = field(default_factory=list)
    domain_hint: str | None = None
    evidence_need: list[str] = field(default_factory=list)
    max_results: int = 5
    timeout_ms: int = 3000


@dataclass
class SourceDocument:
    source_id: str
    title: str
    content: str
    source_type: SourceType = "document"
    authority_level: AuthorityLevel = "medium"
    freshness: Freshness = "acceptable"
    retrieved_at: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class SourceAPIResponse:
    query_id: str
    status: APIStatus = "ok"
    documents: list[SourceDocument] = field(default_factory=list)
    latency_ms: int = 0
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
