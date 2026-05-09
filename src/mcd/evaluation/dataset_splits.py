"""Dataset Splits — splits dataset into train/validation/holdout."""
from __future__ import annotations
import random
from dataclasses import dataclass
from collections import defaultdict
from mcd.evaluation.dataset_schema import BenchmarkExample


@dataclass
class DatasetSplits:
    train_calibration: list[BenchmarkExample]
    validation: list[BenchmarkExample]
    holdout: list[BenchmarkExample]

    @property
    def total(self) -> int:
        return len(self.train_calibration) + len(self.validation) + len(self.holdout)

    def to_dict(self) -> dict:
        return {
            "train_calibration": len(self.train_calibration),
            "validation": len(self.validation),
            "holdout": len(self.holdout),
            "total": self.total,
        }


def split_dataset(
    examples: list[BenchmarkExample],
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    seed: int = 42,
) -> DatasetSplits:
    rng = random.Random(seed)
    by_source: dict[str, list[BenchmarkExample]] = defaultdict(list)
    for ex in examples:
        by_source[ex.source_type].append(ex)

    train, val, holdout = [], [], []

    for source_examples in by_source.values():
        shuffled = list(source_examples)
        rng.shuffle(shuffled)
        n = len(shuffled)
        n_train = max(1, int(n * train_ratio)) if n >= 3 else n
        n_val = max(0, int(n * val_ratio)) if n >= 3 else 0
        train.extend(shuffled[:n_train])
        val.extend(shuffled[n_train:n_train + n_val])
        holdout.extend(shuffled[n_train + n_val:])

    return DatasetSplits(train_calibration=train, validation=val, holdout=holdout)
