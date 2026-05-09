"""Source adapter: abstract + static."""
from __future__ import annotations


class SourceAdapter:
    def fetch(self, query: str) -> list[dict]:
        raise NotImplementedError

    def get_reliability(self) -> float:
        raise NotImplementedError


class StaticSourceAdapter(SourceAdapter):
    def __init__(self, data: list[dict], reliability: float = 0.8) -> None:
        self._data = data
        self._reliability = reliability

    def fetch(self, query: str) -> list[dict]:
        return [d for d in self._data if query.lower() in str(d).lower()]

    def get_reliability(self) -> float:
        return self._reliability
