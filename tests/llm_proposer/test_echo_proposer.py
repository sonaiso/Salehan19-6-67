"""Tests for EchoProposer — deterministic, no API key required."""
from __future__ import annotations

from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import Proposal


class TestEchoProposer:
    def setup_method(self) -> None:
        self.proposer = EchoProposer()

    def test_returns_proposal(self) -> None:
        result = self.proposer.propose("hello")
        assert isinstance(result, Proposal)

    def test_raw_text_is_prefixed_echo(self) -> None:
        result = self.proposer.propose("النار محرقة")
        assert result.raw_text == "ECHO::النار محرقة"

    def test_prompt_preserved(self) -> None:
        result = self.proposer.propose("test prompt")
        assert result.prompt == "test prompt"

    def test_provider_is_echo(self) -> None:
        result = self.proposer.propose("x")
        assert result.provider == "echo"

    def test_model_is_echo_v1(self) -> None:
        result = self.proposer.propose("x")
        assert result.model == "echo-v1"

    def test_deterministic(self) -> None:
        p1 = self.proposer.propose("same prompt")
        p2 = self.proposer.propose("same prompt")
        assert p1.raw_text == p2.raw_text

    def test_different_prompts_different_output(self) -> None:
        p1 = self.proposer.propose("prompt A")
        p2 = self.proposer.propose("prompt B")
        assert p1.raw_text != p2.raw_text

    def test_no_api_key_needed(self, monkeypatch) -> None:
        """EchoProposer must work even when API keys are absent."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result = self.proposer.propose("should still work")
        assert result.raw_text.startswith("ECHO::")
