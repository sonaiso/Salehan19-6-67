"""Dataset loader — loads BenchmarkExample objects from JSONL/JSON files."""
from __future__ import annotations
import json
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample

DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "evaluation"


def load_jsonl(path: Path) -> list[BenchmarkExample]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(BenchmarkExample.from_dict(json.loads(line)))
    return examples


def load_static_gold(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    return load_jsonl(data_dir / "static_gold_ar.jsonl")


def load_adversarial(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    return load_jsonl(data_dir / "adversarial_ar.jsonl")


def load_ambiguity(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    return load_jsonl(data_dir / "ambiguity_ar.jsonl")


def load_calibration(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    return load_jsonl(data_dir / "calibration_ar.jsonl")


def load_all(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    examples = []
    for fname in ["static_gold_ar.jsonl", "adversarial_ar.jsonl", "ambiguity_ar.jsonl", "calibration_ar.jsonl"]:
        p = data_dir / fname
        if p.exists():
            examples.extend(load_jsonl(p))
    return examples
