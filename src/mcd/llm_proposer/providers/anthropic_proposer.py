"""AnthropicProposer — optional LLM proposer backed by the Anthropic API.

The ``anthropic`` package and the ``ANTHROPIC_API_KEY`` environment variable
are *not* required at import time.  Missing dependencies or credentials raise
``RuntimeError`` only when ``propose()`` is called.

Install the optional extra to enable:
    pip install minimal-cognitive-decoder[anthropic]
"""
from __future__ import annotations

import os

from mcd.llm_proposer.base import BaseLLMProposer
from mcd.llm_proposer.types import Proposal


class AnthropicProposer(BaseLLMProposer):
    """LLM proposer backed by Claude models via the Anthropic API."""

    name: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022") -> None:
        self.model = model
        self._client: object = None

    def _init_client(self) -> None:
        try:
            import anthropic  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(
                "The 'anthropic' package is not installed. "
                "Install it with: pip install minimal-cognitive-decoder[anthropic]"
            ) from exc
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Set it before using AnthropicProposer."
            )
        import anthropic  # noqa: PLC0415

        self._client = anthropic.Anthropic(api_key=api_key)

    def propose(self, prompt: str, **kwargs: object) -> Proposal:
        if self._client is None:
            self._init_client()
        assert self._client is not None
        message = self._client.messages.create(  # type: ignore[union-attr]
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text: str = message.content[0].text if message.content else ""
        return Proposal(
            prompt=prompt,
            raw_text=raw_text,
            provider=self.name,
            model=self.model,
            metadata={"anthropic_id": message.id},
        )
