"""Evaluation Runner — orchestrates benchmark evaluation across all layers."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from mcd.evaluation.benchmark_dataset import BenchmarkExample, load_benchmark_examples
from mcd.evaluation.kpi_schema import KPI, build_kpi_registry
from mcd.evaluation.simulation_metrics import EvaluationScore, score_example


@dataclass
class EvaluationReport:
    total_examples: int
    passed: int
    failed: int
    average_score: float
    kpis: list[dict]
    scores: list[EvaluationScore]
    failures: list[str]
    recommendations: list[str]


class EvaluationRunner:
    """Run benchmark examples through FPCL and score results."""

    def __init__(self) -> None:
        self._classifier = None

    def _get_classifier(self):
        if self._classifier is None:
            from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
            self._classifier = FractalPromptClassifier()
        return self._classifier

    def _frame_to_dict(self, frame: Any) -> dict:
        """Convert a PromptFrame to a dict for scoring."""
        return {
            "raw_text": frame.raw_text,
            "intent": frame.intent,
            "root_domain": frame.root_domain,
            "concept_types": frame.concept_types,
            "knowledge_categories": frame.knowledge_categories,
            "judgment_types": frame.judgment_types,
            "evidence_needs": frame.evidence_needs,
            "certainty_policy": frame.certainty_policy,
            "routing_engine": frame.routing_engine,
            "warnings": frame.warnings,
        }

    def run(self, examples: list[BenchmarkExample] | None = None) -> EvaluationReport:
        if examples is None:
            examples = load_benchmark_examples()

        clf = self._get_classifier()
        scores: list[EvaluationScore] = []
        all_failures: list[str] = []

        for ex in examples:
            try:
                frame = clf.classify(ex.input_text)
                frame_dict = self._frame_to_dict(frame)
                score = score_example(
                    example_id=ex.example_id,
                    expected=ex.expected_behavior,
                    mcd_frame_dict=frame_dict,
                    warnings=frame.warnings,
                )
                scores.append(score)
                all_failures.extend(f"{ex.example_id}: {f}" for f in score.failures)
            except Exception as exc:
                all_failures.append(f"{ex.example_id}: exception — {exc}")
                scores.append(EvaluationScore(
                    example_id=ex.example_id,
                    total_score=0.0,
                    dimension_scores={},
                    failures=[str(exc)],
                    warnings=[],
                ))

        avg = sum(s.total_score for s in scores) / max(len(scores), 1)
        passed = sum(1 for s in scores if s.total_score >= 0.5)
        failed = len(scores) - passed

        kpis = [k.to_dict() for k in build_kpi_registry()]

        recommendations: list[str] = []
        if avg < 0.7:
            recommendations.append("Average score below 0.7 — review classifier calibration")
        if failed > len(scores) // 2:
            recommendations.append("More than half of examples failed — expand benchmark analysis")

        return EvaluationReport(
            total_examples=len(examples),
            passed=passed,
            failed=failed,
            average_score=round(avg, 3),
            kpis=kpis,
            scores=scores,
            failures=all_failures,
            recommendations=recommendations,
        )
