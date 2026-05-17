"""ProposerTrace — serialize, persist, and replay governed pipeline runs.

Each run is saved as a JSON artifact under::

    artifacts/llm_proposer/<timestamp>_<VERDICT>.json

Replay:
    answer = ProposerTrace.replay("artifacts/llm_proposer/xxx.json", proposer)

Replay is deterministic when using EchoProposer because the raw_text is
reconstructed from the stored prompt and the governance gates are stateless.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import GovernedAnswer, Proposal

_ARTIFACTS_DIR = Path("artifacts") / "llm_proposer"


def _ensure_artifacts_dir() -> Path:
    artifacts_dir = _ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir


def _answer_to_dict(answer: GovernedAnswer) -> dict[str, object]:
    return {
        "verdict": answer.verdict,
        "evidence": answer.evidence,
        "reverse_trace": answer.reverse_trace,
        "violated_rules": answer.violated_rules,
        "created_at": answer.created_at,
        "proposal": {
            "prompt": answer.proposal.prompt,
            "raw_text": answer.proposal.raw_text,
            "provider": answer.proposal.provider,
            "model": answer.proposal.model,
            "metadata": answer.proposal.metadata,
        },
        # Preserved original caller inputs for deterministic replay
        "_replay_inputs": {
            "evidence": answer.evidence,
            "reverse_trace": answer.reverse_trace,
        },
    }


def save(answer: GovernedAnswer, *, base_dir: Path | None = None) -> Path:
    """Persist *answer* as a JSON artifact and return the file path."""
    directory = base_dir if base_dir is not None else _ensure_artifacts_dir()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    filename = f"{timestamp}_{answer.verdict}.json"
    path = directory / filename
    with path.open("w", encoding="utf-8") as fh:
        json.dump(_answer_to_dict(answer), fh, ensure_ascii=False, indent=2)
    return path


def load(path: str | Path) -> dict[str, object]:
    """Load a raw artifact dict from *path*."""
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[return-value]


def replay(path: str | Path, governor: AFJGGovernor | None = None) -> GovernedAnswer:
    """Replay a saved artifact and return a fresh GovernedAnswer.

    For deterministic replay use EchoProposer:
    the raw_text stored in the artifact is used directly as the proposal,
    so the governance verdict will be identical.
    """
    data = load(path)
    prop_data = data["proposal"]  # type: ignore[index]
    proposal = Proposal(
        prompt=str(prop_data["prompt"]),  # type: ignore[index]
        raw_text=str(prop_data["raw_text"]),  # type: ignore[index]
        provider=str(prop_data["provider"]),  # type: ignore[index]
        model=str(prop_data["model"]),  # type: ignore[index]
        metadata=dict(prop_data.get("metadata", {})),  # type: ignore[index,arg-type]
    )
    # Restore original caller-supplied inputs for a deterministic replay
    replay_inputs = data.get("_replay_inputs", {})  # type: ignore[union-attr]
    original_evidence: list[str] = list(replay_inputs.get("evidence", data.get("evidence", [])))  # type: ignore[union-attr]
    original_reverse_trace: list[str] = list(replay_inputs.get("reverse_trace", []))  # type: ignore[union-attr]
    gov = governor if governor is not None else AFJGGovernor()
    return gov.govern(
        proposal,
        evidence=original_evidence,
        reverse_trace=original_reverse_trace,
    )
