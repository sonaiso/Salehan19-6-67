"""Providers sub-package for the Governed LLM Proposer.

Available proposers:
- EchoProposer   — deterministic, no API key (default for CI/tests)
- OpenAIProposer — GPT models; requires openai extra + OPENAI_API_KEY
- AnthropicProposer — Claude models; requires anthropic extra + ANTHROPIC_API_KEY
"""
from __future__ import annotations

from mcd.llm_proposer.providers.echo import EchoProposer

__all__ = ["EchoProposer"]
