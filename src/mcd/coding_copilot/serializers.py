"""Serialization helpers for coding copilot kernel objects."""
from __future__ import annotations

import json

from mcd.coding_copilot.coding_judgment import CodingJudgment


def coding_judgment_to_dict(j: CodingJudgment) -> dict:
    return j.to_dict()


def coding_judgment_to_json(j: CodingJudgment) -> str:
    return json.dumps(coding_judgment_to_dict(j), ensure_ascii=False, indent=2)
