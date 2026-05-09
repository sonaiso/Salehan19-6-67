"""CurriculumDataset — loads and manages curriculum JSONL files."""
from __future__ import annotations

import json
from pathlib import Path

from .cognitive_unit import CognitiveUnit
from .reality_frame import RealityFrame, RelationTriple
from .curriculum_schema import LEVEL_NAMES


_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "curriculum"


def _build_frame(data: dict) -> RealityFrame:
    frame_data = data.get("expected_frame", {})
    relations = [
        RelationTriple(
            source=r["source"],
            relation=r["relation"],
            target=r["target"],
            qualifier=r.get("qualifier"),
        )
        for r in frame_data.get("relations", [])
    ]
    return RealityFrame(
        things=frame_data.get("things", []),
        properties=frame_data.get("properties", []),
        actions=frame_data.get("actions", []),
        agents=frame_data.get("agents", []),
        patients=frame_data.get("patients", []),
        instruments=frame_data.get("instruments", []),
        times=frame_data.get("times", []),
        places=frame_data.get("places", []),
        causes=frame_data.get("causes", []),
        effects=frame_data.get("effects", []),
        relations=relations,
        evidence_need=frame_data.get("evidence_need", []),
        certainty_policy=frame_data.get("certainty_policy", "probable_knowledge"),
        warnings=frame_data.get("warnings", []),
    )


def _load_jsonl(path: Path) -> list[CognitiveUnit]:
    units = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            frame = _build_frame(data)
            units.append(CognitiveUnit(
                unit_id=data["unit_id"],
                input_text=data["input_text"],
                level=data["level"],
                target_layer=data["target_layer"],
                expected_frame=frame,
                expected_warnings=data.get("expected_warnings", []),
                forbidden_confusions=data.get("forbidden_confusions", []),
                evidence_need=data.get("evidence_need", []),
                certainty_policy=data.get("certainty_policy", "probable_knowledge"),
                difficulty=data.get("difficulty", "medium"),
                tags=data.get("tags", []),
                metadata=data.get("metadata", {}),
            ))
    return units


class CurriculumDataset:
    """Manages curriculum JSONL data files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._dir = data_dir or _DATA_DIR

    def load_level(self, level: int) -> list[CognitiveUnit]:
        name = LEVEL_NAMES.get(level, f"level_{level:02d}")
        pattern = f"level_{level:02d}_{name}_ar.jsonl"
        path = self._dir / pattern
        if not path.exists():
            matches = list(self._dir.glob(f"level_{level:02d}_*.jsonl"))
            if not matches:
                return []
            path = matches[0]
        return _load_jsonl(path)

    def load_all(self) -> list[CognitiveUnit]:
        units = []
        for level in range(1, 9):
            units.extend(self.load_level(level))
        return units

    def load_levels(self, levels: list[int]) -> list[CognitiveUnit]:
        units = []
        for level in levels:
            units.extend(self.load_level(level))
        return units

    def count_by_level(self) -> dict[int, int]:
        return {level: len(self.load_level(level)) for level in range(1, 9)}
