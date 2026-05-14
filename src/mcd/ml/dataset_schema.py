"""Schema loaders and constants for answer-birth ML training data."""
from __future__ import annotations

import json
from pathlib import Path

from mcd.core.epistemic_rank import EpistemicRank

THINKING_EVIDENCE_RANK_TOKENS: tuple[str, ...] = ("none", "low", "medium", "high", "governed")
CORE_EVIDENCE_RANK_TOKENS: tuple[str, ...] = tuple(
    rank.name.lower() for rank in EpistemicRank if rank is not EpistemicRank.FINAL_JUDGMENT
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _schema_dir() -> Path:
    return _repo_root() / "data" / "schemas"


def load_json_file(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_answer_birth_training_example_schema() -> dict:
    return load_json_file(_schema_dir() / "answer_birth_training_example.schema.json")


def load_concept_graph_schema() -> dict:
    return load_json_file(_schema_dir() / "concept_graph.schema.json")


def load_governed_trace_schema() -> dict:
    return load_json_file(_schema_dir() / "governed_trace.schema.json")


def load_nabhani_features_schema() -> dict:
    return load_json_file(_schema_dir() / "nabhani_features.schema.json")
