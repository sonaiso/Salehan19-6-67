"""OpenAIProposer — optional LLM proposer backed by the OpenAI API.

The ``openai`` package and the ``OPENAI_API_KEY`` environment variable are
*not* required at import time.  Missing dependencies or credentials raise
``RuntimeError`` only when ``propose()`` is called, keeping CI clean.

Install the optional extra to enable:
    pip install minimal-cognitive-decoder[openai]
"""
from __future__ import annotations

import os

from mcd.llm_proposer.base import BaseLLMProposer
from mcd.llm_proposer.types import Proposal


class OpenAIProposer(BaseLLMProposer):
    """LLM proposer backed by GPT models via the OpenAI API."""

    name: str = "openai"
    model: str = "gpt-4o"

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model
        self._client: object = None  # lazy-initialised in propose()

    def _init_client(self) -> None:
        try:
            import openai  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(
                "The 'openai' package is not installed. "
                "Install it with: pip install minimal-cognitive-decoder[openai]"
            ) from exc
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it before using OpenAIProposer."
            )
        self._client = openai.OpenAI(api_key=api_key)

    def propose(self, prompt: str, **kwargs: object) -> Proposal:
        if self._client is None:
            self._init_client()
        assert self._client is not None
        import openai  # noqa: PLC0415

        completion = self._client.chat.completions.create(  # type: ignore[union-attr]
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text: str = completion.choices[0].message.content or ""
        return Proposal(
            prompt=prompt,
            raw_text=raw_text,
            provider=self.name,
            model=self.model,
            metadata={"openai_id": completion.id},
        )
