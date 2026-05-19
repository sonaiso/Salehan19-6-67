"""AFU theory index — declarative map from theory layers to gate ids.

PR 2 ships this index *empty but structured*. Later PRs populate the
YAML with concrete entries, but the schema is fixed here so reviewers
can mechanically check that new gates are declared in a single place.
"""
from __future__ import annotations

from pathlib import Path

THEORY_INDEX_PATH: Path = (Path(__file__).parent / "theory_to_gate_map.yaml").resolve()

__all__ = ["THEORY_INDEX_PATH"]
