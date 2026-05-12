"""Run empirical governance benchmarks and emit readiness artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from mcd.evaluation.benchmark_runner import run_empirical_benchmarks
    from mcd.evaluation.readiness_scoring import (
        build_readiness_report,
        readiness_report_json,
        readiness_report_markdown,
    )

    benchmark_report = run_empirical_benchmarks()
    readiness_report = build_readiness_report(benchmark_report.metrics)

    benchmark_results_dir = repo_root / "benchmarks" / "results"
    benchmark_results_dir.mkdir(parents=True, exist_ok=True)
    latest_path = benchmark_results_dir / "latest.json"
    latest_path.write_text(
        json.dumps(benchmark_report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    evaluation_dir = repo_root / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    (evaluation_dir / "readiness_report.json").write_text(
        readiness_report_json(readiness_report) + "\n", encoding="utf-8"
    )
    (evaluation_dir / "readiness_report.md").write_text(
        readiness_report_markdown(readiness_report), encoding="utf-8"
    )

    print(f"benchmarks: {latest_path}")
    print("evaluation: readiness_report.json, readiness_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
