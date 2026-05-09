"""Database adapter: abstract + in-memory."""
from __future__ import annotations


class DatabaseAdapter:
    def store(self, key: str, value: dict) -> None:
        raise NotImplementedError

    def retrieve(self, key: str) -> dict | None:
        raise NotImplementedError

    def list_keys(self, prefix: str = "") -> list[str]:
        raise NotImplementedError


class InMemoryDatabaseAdapter(DatabaseAdapter):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def store(self, key: str, value: dict) -> None:
        self._store[key] = value

    def retrieve(self, key: str) -> dict | None:
        return self._store.get(key)

    def list_keys(self, prefix: str = "") -> list[str]:
        return [k for k in self._store if k.startswith(prefix)]
