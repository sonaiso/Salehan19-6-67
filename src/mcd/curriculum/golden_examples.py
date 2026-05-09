"""Golden examples registry — reference examples for curriculum validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json


_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "curriculum"


@dataclass
class GoldenExample:
    example_id: str
    input_text: str
    expected_nodes: list[dict]
    expected_edges: list[dict]
    expected_domains: list[str]
    evidence_need: list[str]
    certainty_policy: str
    forbidden_confusions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "example_id": self.example_id,
            "input_text": self.input_text,
            "expected_nodes": self.expected_nodes,
            "expected_edges": self.expected_edges,
            "expected_domains": self.expected_domains,
            "evidence_need": self.evidence_need,
            "certainty_policy": self.certainty_policy,
            "forbidden_confusions": self.forbidden_confusions,
            "tags": self.tags,
        }


def load_golden_examples() -> list[GoldenExample]:
    path = _DATA_DIR / "golden_examples_ar.jsonl"
    if not path.exists():
        return []
    examples = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        examples.append(GoldenExample(
            example_id=d["example_id"],
            input_text=d["input_text"],
            expected_nodes=d.get("expected_nodes", []),
            expected_edges=d.get("expected_edges", []),
            expected_domains=d.get("expected_domains", []),
            evidence_need=d.get("evidence_need", []),
            certainty_policy=d.get("certainty_policy", "probable_knowledge"),
            forbidden_confusions=d.get("forbidden_confusions", []),
            tags=d.get("tags", []),
        ))
    return examples
