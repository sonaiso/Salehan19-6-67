"""Calibration dataset utilities."""
from __future__ import annotations
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample

DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "evaluation"


def load_calibration_examples(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    from mcd.evaluation.dataset_loader import load_calibration
    return load_calibration(data_dir)


def get_calibration_by_dimension(examples: list[BenchmarkExample], dimension: str) -> list[BenchmarkExample]:
    return [ex for ex in examples if dimension in ex.tags]


def get_shari_calibration(examples: list[BenchmarkExample]) -> list[BenchmarkExample]:
    return get_calibration_by_dimension(examples, "shari")


def get_ambiguity_calibration(examples: list[BenchmarkExample]) -> list[BenchmarkExample]:
    return [ex for ex in examples if "ambiguous" in ex.tags or ex.source_type == "ambiguity"]


def get_epistemic_calibration(examples: list[BenchmarkExample]) -> list[BenchmarkExample]:
    return get_calibration_by_dimension(examples, "epistemic")
