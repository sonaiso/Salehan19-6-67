"""Coverage Matrix — measures dataset coverage across all dimensions."""
from __future__ import annotations
from dataclasses import dataclass, field
from mcd.evaluation.dataset_schema import BenchmarkExample

EXPECTED_JUDGMENT_TYPES = {"epistemic", "technical", "value", "shari", "practical", "linguistic", "ambiguous", "analogy", "metaphor", "usuli"}
EXPECTED_DIFFICULTIES = {"easy", "medium", "hard", "adversarial"}
EXPECTED_CERTAINTY_POLICIES = {"near_certainty", "strong_knowledge", "probable_knowledge", "hypothesis", "suspend"}
EXPECTED_SOURCE_TYPES = {"static_gold", "dynamic_generated", "adversarial", "ambiguity", "calibration"}


@dataclass
class DimensionCoverage:
    dimension: str
    covered: set[str]
    expected: set[str]

    @property
    def coverage_ratio(self) -> float:
        if not self.expected:
            return 1.0
        return len(self.covered & self.expected) / len(self.expected)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "covered": sorted(self.covered),
            "expected": sorted(self.expected),
            "coverage_ratio": round(self.coverage_ratio, 4),
        }


@dataclass
class CoverageReport:
    total_examples: int
    dimension_coverages: list[DimensionCoverage] = field(default_factory=list)
    coverage_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "total_examples": self.total_examples,
            "coverage_score": round(self.coverage_score, 4),
            "dimensions": [d.to_dict() for d in self.dimension_coverages],
        }


class CoverageMatrix:
    def __init__(self, examples: list[BenchmarkExample]):
        self.examples = examples

    def compute(self) -> CoverageReport:
        if not self.examples:
            return CoverageReport(total_examples=0, coverage_score=0.0)

        judgment_types_seen: set[str] = set()
        difficulties_seen: set[str] = set()
        certainty_policies_seen: set[str] = set()
        source_types_seen: set[str] = set()

        for ex in self.examples:
            judgment_types_seen.update(ex.expected_judgment_types.keys())
            difficulties_seen.add(ex.difficulty)
            certainty_policies_seen.add(ex.expected_certainty_policy)
            source_types_seen.add(ex.source_type)

        dims = [
            DimensionCoverage("judgment_type", judgment_types_seen, EXPECTED_JUDGMENT_TYPES),
            DimensionCoverage("difficulty", difficulties_seen, EXPECTED_DIFFICULTIES),
            DimensionCoverage("certainty_policy", certainty_policies_seen, EXPECTED_CERTAINTY_POLICIES),
            DimensionCoverage("source_type", source_types_seen, EXPECTED_SOURCE_TYPES),
        ]

        coverage_score = sum(d.coverage_ratio for d in dims) / len(dims)

        return CoverageReport(
            total_examples=len(self.examples),
            dimension_coverages=dims,
            coverage_score=coverage_score,
        )
