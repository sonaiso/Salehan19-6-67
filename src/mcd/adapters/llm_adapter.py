"""LLM adapter interface and mock."""
from __future__ import annotations


class LLMAdapter:
    """Abstract LLM adapter. LLM is a suggester, NOT the final judge."""

    def generate_candidates(self, prompt: str) -> list[dict]:
        raise NotImplementedError

    def summarize(self, text: str) -> str:
        raise NotImplementedError

    def compare(self, a: str, b: str) -> dict:
        raise NotImplementedError


class MockLLMAdapter(LLMAdapter):
    def generate_candidates(self, prompt: str) -> list[dict]:
        return [{"candidate": prompt, "confidence": 0.5}]

    def summarize(self, text: str) -> str:
        return f"[Mock summary of: {text[:50]}]"

    def compare(self, a: str, b: str) -> dict:
        return {"similar": a == b, "confidence": 0.5}
