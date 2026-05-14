"""Simple JSON serialization helpers for governed ML datasets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def dump_json(payload: dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
