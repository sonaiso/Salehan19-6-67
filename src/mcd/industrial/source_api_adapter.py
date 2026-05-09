"""Source API Adapter — abstract interface for source retrieval."""
from __future__ import annotations

from abc import ABC, abstractmethod

from mcd.industrial.api_contract import SourceAPIResponse, SourceQuery


class BaseSourceAPIAdapter(ABC):
    @abstractmethod
    def search(self, query: SourceQuery) -> SourceAPIResponse:
        ...


class NullSourceAPIAdapter(BaseSourceAPIAdapter):
    """Always returns empty — useful when no API is configured."""

    def search(self, query: SourceQuery) -> SourceAPIResponse:
        return SourceAPIResponse(
            query_id=query.query_id,
            status="empty",
            documents=[],
            latency_ms=0,
            warnings=["no_source_api_configured"],
        )
