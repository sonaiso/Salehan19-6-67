"""Generate synthetic governed answer-birth dataset splits and stats."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcd.ml.synthetic_generator import generate_synthetic_answer_birth_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "generated" / "answer_birth"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic governed answer-birth dataset.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for train/validation/test JSONL and stats.json")
    parser.add_argument("--seed", type=int, default=97, help="Deterministic generation seed")
    parser.add_argument("--total", type=int, default=10_000, help="Total examples to generate")
    parser.add_argument("--train", type=int, default=8000, help="Train split size")
    parser.add_argument("--validation", type=int, default=1000, help="Validation split size")
    parser.add_argument("--test", type=int, default=1000, help="Test split size")
    args = parser.parse_args()

    if args.train + args.validation + args.test != args.total:
        raise SystemExit("split sizes must sum to --total")

    report = generate_synthetic_answer_birth_dataset(
        output_dir=Path(args.output_dir),
        seed=args.seed,
        total_examples=args.total,
        train_size=args.train,
        validation_size=args.validation,
        test_size=args.test,
    )
    print(json.dumps(report["stats"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
