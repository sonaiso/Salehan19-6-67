from __future__ import annotations

import json
from pathlib import Path


def _mapping_by_obligation() -> dict[str, dict]:
    payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))
    return {item["obligation"]: item for item in payload["mapping"]}


def test_rank_soundness_lean_file_contains_required_contracts():
    path = Path("research/formal/lean/RankSoundness.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")

    required_tokens = [
        "inductive EpistemicRank",
        "def requiredRank",
        "def rankLeq",
        "theorem rank_soundness",
        "theorem insufficient_rank_blocks_certificate",
    ]
    for token in required_tokens:
        assert token in text
    assert "sorry" not in text


def test_rank_soundness_theorems_and_mapping_exist():
    mapping = _mapping_by_obligation()

    for obligation in ("RankSoundness", "InsufficientRankBlocksCertificate"):
        assert obligation in mapping
        assert mapping[obligation]["runtime_invariant_name"]
        assert mapping[obligation]["python_file"].endswith(".py")
        assert mapping[obligation]["test_file"].endswith("test_formal_rank_soundness_track.py")
        assert mapping[obligation]["lean_file"].endswith("RankSoundness.lean")
        assert "minimal" in mapping[obligation]["claim_boundary"].lower()


def test_rank_soundness_claim_boundary_is_honest_and_non_agi():
    payload = Path("research/formal/proof_mapping.json").read_text(encoding="utf-8").lower()
    roadmap = Path("research/theorem_roadmap.md").read_text(encoding="utf-8").lower()

    forbidden = ["full mathematical proof of the whole project", "consciousness", "agi"]
    assert not any(token in payload for token in forbidden)
    assert "no consciousness or agi claim" in roadmap
