"""Tests for EvaluationRunner."""
from mcd.evaluation.evaluation_runner import EvaluationRunner, EvaluationReport
from mcd.evaluation.benchmark_dataset import load_benchmark_examples


def test_evaluation_runner_runs():
    runner = EvaluationRunner()
    report = runner.run()
    assert isinstance(report, EvaluationReport)


def test_evaluation_runner_total_examples():
    runner = EvaluationRunner()
    report = runner.run()
    assert report.total_examples == 10


def test_evaluation_runner_scores_all():
    runner = EvaluationRunner()
    report = runner.run()
    assert len(report.scores) == report.total_examples


def test_evaluation_runner_average_score_range():
    runner = EvaluationRunner()
    report = runner.run()
    assert 0.0 <= report.average_score <= 1.0


def test_evaluation_runner_kpis_present():
    runner = EvaluationRunner()
    report = runner.run()
    assert len(report.kpis) >= 20


def test_evaluation_runner_passed_plus_failed():
    runner = EvaluationRunner()
    report = runner.run()
    assert report.passed + report.failed == report.total_examples


def test_evaluation_runner_custom_examples():
    from mcd.evaluation.benchmark_dataset import BenchmarkExample
    examples = [
        BenchmarkExample(
            example_id="TEST-01",
            input_text="النار تحرق",
            task_type="test",
            expected_behavior={"certainty_policy": ["near_certainty", "strong_knowledge"]},
        )
    ]
    runner = EvaluationRunner()
    report = runner.run(examples)
    assert report.total_examples == 1
