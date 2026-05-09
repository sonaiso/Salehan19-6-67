"""JSON serializers for curriculum objects."""
from __future__ import annotations

import json

from .cognitive_unit import CognitiveUnit
from .reality_frame import RealityFrame, RelationTriple


def relation_triple_to_dict(rt: RelationTriple) -> dict:
    return rt.to_dict()


def reality_frame_to_dict(rf: RealityFrame) -> dict:
    return rf.to_dict()


def cognitive_unit_to_dict(cu: CognitiveUnit) -> dict:
    return cu.to_dict()


def cognitive_unit_to_json(cu: CognitiveUnit, indent: int | None = 2) -> str:
    return json.dumps(cu.to_dict(), ensure_ascii=False, indent=indent)


def cognitive_units_to_jsonl(units: list[CognitiveUnit]) -> str:
    lines = [json.dumps(u.to_dict(), ensure_ascii=False) for u in units]
    return "\n".join(lines)
