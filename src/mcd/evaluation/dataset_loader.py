"""Dataset loader — loads BenchmarkExample objects from JSONL/JSON files."""
from __future__ import annotations
import json
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample, WebEvaluatorExample

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


def load_web_evaluator_jsonl(path: Path) -> list[WebEvaluatorExample]:
    """Load the web evaluator prompt dataset (WEB-001 … WEB-085+)."""
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(WebEvaluatorExample.from_dict(json.loads(line)))
    return examples


def load_web_evaluator(data_dir: Path = DEFAULT_DATA_DIR) -> list[WebEvaluatorExample]:
    """Load data/evaluation/web_evaluator_prompts_ar_dataset.jsonl."""
    return load_web_evaluator_jsonl(data_dir / "web_evaluator_prompts_ar_dataset.jsonl")
