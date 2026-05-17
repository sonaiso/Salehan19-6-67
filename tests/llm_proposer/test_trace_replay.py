"""Tests that saving and replaying a trace produces the same verdict."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from mcd.llm_proposer import trace as trace_module
from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import GovernedAnswer


class TestTraceReplay:
    def setup_method(self) -> None:
        self.governor = AFJGGovernor()
        self.proposer = EchoProposer()

    def _run_pipeline(
        self,
        prompt: str,
        evidence: list[str] | None = None,
        reverse_trace: list[str] | None = None,
    ) -> GovernedAnswer:
        pipeline = GovernedProposalPipeline(self.proposer, self.governor)
        return pipeline.run(prompt, evidence=evidence, reverse_trace=reverse_trace)

    def test_replay_hypothesis_matches_original(self) -> None:
        original = self._run_pipeline("simple claim")
        assert original.verdict == "HYPOTHESIS"

        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(original, base_dir=Path(tmpdir))
            replayed = trace_module.replay(saved_path, self.governor)

        assert replayed.verdict == original.verdict

    def test_replay_certificate_matches_original(self) -> None:
        evidence = ["observation 1", "observation 2"]
        rt = ["step 1", "raw_text_units: النار محرقة", "step 2"]
        original = self._run_pipeline("النار محرقة", evidence=evidence, reverse_trace=rt)
        assert original.verdict == "CERTIFICATE"

        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(original, base_dir=Path(tmpdir))
            replayed = trace_module.replay(saved_path, self.governor)

        assert replayed.verdict == original.verdict

    def test_replay_zero_matches_original(self) -> None:
        original = self._run_pipeline("")
        assert original.verdict == "ZERO"

        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(original, base_dir=Path(tmpdir))
            replayed = trace_module.replay(saved_path, self.governor)

        assert replayed.verdict == original.verdict

    def test_saved_artifact_is_valid_json(self) -> None:
        answer = self._run_pipeline("test claim")
        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(answer, base_dir=Path(tmpdir))
            with open(saved_path, encoding="utf-8") as fh:
                data = json.load(fh)
        assert "verdict" in data
        assert "proposal" in data
        assert "evidence" in data
        assert "reverse_trace" in data

    def test_artifact_filename_contains_verdict(self) -> None:
        answer = self._run_pipeline("test claim")
        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(answer, base_dir=Path(tmpdir))
            assert answer.verdict in saved_path.name

    def test_replay_preserves_proposal_prompt(self) -> None:
        original = self._run_pipeline("specific prompt text")
        with tempfile.TemporaryDirectory() as tmpdir:
            saved_path = trace_module.save(original, base_dir=Path(tmpdir))
            replayed = trace_module.replay(saved_path, self.governor)
        assert replayed.proposal.prompt == original.proposal.prompt
