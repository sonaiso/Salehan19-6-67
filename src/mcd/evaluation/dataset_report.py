"""Dataset Report — generates Markdown reports for the dataset."""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from mcd.evaluation.dataset_schema import BenchmarkExample
from mcd.evaluation.coverage_matrix import CoverageMatrix


@dataclass
class DatasetReport:
    examples: list[BenchmarkExample]

    def _count_by(self, key_fn) -> dict[str, int]:
        c: Counter = Counter()
        for ex in self.examples:
            c[key_fn(ex)] += 1
        return dict(c.most_common())

    def generate_markdown(self) -> str:
        total = len(self.examples)
        by_source = self._count_by(lambda ex: ex.source_type)
        by_difficulty = self._count_by(lambda ex: ex.difficulty)
        by_policy = self._count_by(lambda ex: ex.expected_certainty_policy)

        jt_counter: Counter = Counter()
        for ex in self.examples:
            for jt in ex.expected_judgment_types:
                jt_counter[jt] += 1

        tag_counter: Counter = Counter()
        for ex in self.examples:
            for t in ex.tags:
                tag_counter[t] += 1

        coverage = CoverageMatrix(self.examples).compute()

        lines = [
            "# Dataset Report",
            "",
            "## 1. Overview",
            f"- Total examples: **{total}**",
            f"- Coverage score: **{coverage.coverage_score:.2%}**",
            "",
            "## 2. Source Type Distribution",
        ]
        for src, cnt in by_source.items():
            lines.append(f"- {src}: {cnt}")

        lines += ["", "## 3. Difficulty Distribution"]
        for diff, cnt in by_difficulty.items():
            lines.append(f"- {diff}: {cnt}")

        lines += ["", "## 4. Certainty Policy Distribution"]
        for policy, cnt in by_policy.items():
            lines.append(f"- {policy}: {cnt}")

        lines += ["", "## 5. Judgment Type Distribution"]
        for jt, cnt in jt_counter.most_common():
            lines.append(f"- {jt}: {cnt}")

        lines += ["", "## 6. Tag Distribution (top 20)"]
        for tag, cnt in tag_counter.most_common(20):
            lines.append(f"- {tag}: {cnt}")

        lines += ["", "## 7. Coverage Matrix"]
        for dim in coverage.dimension_coverages:
            lines.append(f"- {dim.dimension}: {dim.coverage_ratio:.2%} ({len(dim.covered)}/{len(dim.expected)})")

        lines += ["", "## 8. Shari Examples"]
        shari = [ex for ex in self.examples if "shari" in ex.expected_judgment_types]
        lines.append(f"- Count: {len(shari)}")
        shari_with_warning = [ex for ex in shari if "shari_evidence_required" in ex.required_warnings]
        lines.append(f"- With shari_evidence_required warning: {len(shari_with_warning)}")

        lines += ["", "## 9. Ambiguous Examples"]
        ambig = [ex for ex in self.examples if ex.expected_certainty_policy == "suspend"]
        lines.append(f"- Count (suspend policy): {len(ambig)}")

        lines += ["", "## 10. Adversarial Examples"]
        adv = [ex for ex in self.examples if ex.source_type == "adversarial" or ex.difficulty == "adversarial"]
        lines.append(f"- Count: {len(adv)}")

        lines += ["", "## 11. Recommendations"]
        if total < 250:
            lines.append("- ⚠️ Dataset has fewer than 250 examples. Consider expanding.")
        if coverage.coverage_score < 0.80:
            lines.append(f"- ⚠️ Coverage score {coverage.coverage_score:.2%} is below 0.80 threshold.")
        else:
            lines.append(f"- ✅ Coverage score {coverage.coverage_score:.2%} meets 0.80 threshold.")

        return "\n".join(lines)
