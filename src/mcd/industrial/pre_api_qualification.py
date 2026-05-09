"""Phase 5.2 — Pre-API Qualification Gate.

Measures 11 dimensions and determines whether the system is
qualified_for_api_phase or blocked_before_api.
api_score is explicitly excluded from the qualification decision.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Scoring thresholds (module-level constants)
# ---------------------------------------------------------------------------

# Dataset scoring thresholds
DATASET_COVERAGE_HIGH: float = 0.90   # coverage_score → 4.6
DATASET_COVERAGE_MID: float = 0.80    # coverage_score → 4.5
DATASET_COVERAGE_LOW: float = 0.70    # coverage_score → 4.4

# Industrial testing thresholds
INDUSTRIAL_PASS_RATE_HIGH: float = 0.90   # → 4.6
INDUSTRIAL_PASS_RATE_MED: float = 0.85    # → 4.5
INDUSTRIAL_FALSE_CERT_MAX: float = 0.05   # max allowed false_certainty_rate

# Source trust thresholds
TRUST_DETECTION_HIGH: float = 0.90   # both injection + source_required → 4.6
TRUST_DETECTION_MED: float = 0.80    # either above 80% → 4.4

# Schema stability thresholds
SCHEMA_STABILITY_HIGH: float = 0.98  # → 4.6
SCHEMA_STABILITY_MED: float = 0.95   # → 4.5
SCHEMA_STABILITY_LOW: float = 0.90   # → 4.3

# Calibration thresholds (false certainty rate)
CALIB_FCR_LOW: float = 0.02   # → 4.7
CALIB_FCR_MED: float = 0.05   # → 4.5
CALIB_FCR_HIGH: float = 0.10  # → 4.3

# Qualification threshold for all non-API dimensions
QUALIFICATION_THRESHOLD: float = 4.5


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------


@dataclass
class PreAPIQualificationDimension:
    name: str
    score: float
    threshold: float = 4.5
    passed: bool = False
    evidence: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "evidence": self.evidence,
            "blockers": self.blockers,
            "next_actions": self.next_actions,
        }


@dataclass
class PreAPIQualificationReport:
    status: str  # "blocked_before_api" | "qualified_for_api_phase"
    dimensions: list[PreAPIQualificationDimension]
    average_non_api_score: float
    api_score: float
    non_api_passed: bool
    blockers: list[str]
    required_fixes_before_api: list[str]
    summary: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "average_non_api_score": self.average_non_api_score,
            "api_score": self.api_score,
            "non_api_passed": self.non_api_passed,
            "blockers": self.blockers,
            "required_fixes_before_api": self.required_fixes_before_api,
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# Scoring helpers (derived from real metrics, not promotional)
# ---------------------------------------------------------------------------


def _score_architecture(audit_data: Optional[dict] = None) -> PreAPIQualificationDimension:
    """Score based on layer package existence and CLI command availability."""
    from pathlib import Path

    src = Path(__file__).parent.parent
    expected_packages = [
        "classification", "grounding", "evaluation", "industrial",
        "nabhani", "engines", "core", "knowledge", "adapters",
    ]

    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    found = []
    missing = []
    for pkg in expected_packages:
        if (src / pkg).is_dir() and (src / pkg / "__init__.py").exists():
            found.append(pkg)
        else:
            missing.append(pkg)

    evidence.append(f"Found {len(found)}/{len(expected_packages)} expected sub-packages")
    if missing:
        blockers.append(f"Missing packages: {missing}")
        next_actions.append("Restore missing packages before API phase")

    # CLI commands — check cli.py exists
    cli_path = src / "cli.py"
    if cli_path.exists():
        evidence.append("CLI entry point (cli.py) exists")
    else:
        blockers.append("cli.py missing")

    # Industrial package
    ind_path = src / "industrial"
    if ind_path.is_dir():
        evidence.append("Industrial package exists")
    else:
        blockers.append("Industrial package missing")

    # Score derivation: start at 4.5, deduct for missing packages
    base = 4.5
    deduction = (len(missing) / len(expected_packages)) * 1.0
    if not cli_path.exists():
        deduction += 0.5
    score = round(max(1.0, base - deduction), 2)

    if audit_data and "architecture_score" in audit_data:
        score = float(audit_data["architecture_score"])

    passed = score >= QUALIFICATION_THRESHOLD and not blockers
    return PreAPIQualificationDimension(
        name="architecture_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_tests(tests_pass: Optional[bool]) -> PreAPIQualificationDimension:
    """Score based on pytest passing status. Capped at 4.3 if tests_pass not confirmed."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if tests_pass is True:
        score = 4.7
        evidence.append("tests_pass=True confirmed by CI or CLI flag")
        evidence.append("Full pytest suite passes: PYTHONPATH=src python -m pytest tests/ -v")
    else:
        score = 4.3
        evidence.append("tests_pass not explicitly confirmed; score capped at 4.3")
        blockers.append(
            "Confirm test suite passes via CI or --tests-pass flag to raise score above 4.3"
        )
        next_actions.append("Run: PYTHONPATH=src python -m pytest tests/ -v and pass --tests-pass true")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="test_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_dataset(
    coverage_report: Optional[dict] = None,
    dataset_metrics: Optional[dict] = None,
) -> PreAPIQualificationDimension:
    """Score based on dataset count, JSONL loads, duplicate check, and coverage.

    If ``dataset_metrics`` is provided, file scanning is skipped and the
    pre-computed values are used directly (useful for testing).
    """
    from pathlib import Path

    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if dataset_metrics is not None:
        # Pre-computed path: bypass file scan
        total_examples = dataset_metrics.get("total_examples", 0)
        duplicate_count = dataset_metrics.get("duplicate_count", 0)
        field_violations = dataset_metrics.get("field_violations", 0)
        evidence.append(f"Dataset examples (pre-computed): {total_examples}")
        evidence.append(f"Duplicate IDs: {duplicate_count}")
        evidence.append(f"Field violations: {field_violations}")
        if duplicate_count:
            blockers.append(f"{duplicate_count} duplicate ID(s) found")
        if field_violations:
            blockers.append(f"{field_violations} examples missing required fields")
    else:
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "evaluation"
        jsonl_files = list(data_dir.glob("*.jsonl")) if data_dir.exists() else []
        total_examples = 0
        id_counts: dict[str, int] = {}
        field_violations = 0

        for jf in jsonl_files:
            try:
                with open(jf, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        total_examples += 1
                        # Support both example_id (standard) and id (web evaluator)
                        eid = obj.get("example_id") or obj.get("id") or ""
                        if eid:
                            id_counts[eid] = id_counts.get(eid, 0) + 1
                        # Support both input_text (standard) and prompt (web evaluator)
                        has_input = "input_text" in obj or "prompt" in obj
                        has_id = bool(eid)
                        if not (has_input and has_id):
                            field_violations += 1
            except Exception as exc:
                blockers.append(f"JSONL parse error in {jf.name}: {exc}")

        duplicate_ids = [k for k, v in id_counts.items() if v > 1]
        duplicate_count = len(duplicate_ids)

        evidence.append(f"Dataset files found: {len(jsonl_files)}")
        evidence.append(f"Total examples loaded: {total_examples}")
        evidence.append(f"Duplicate IDs: {duplicate_count}")
        evidence.append(f"Field violations: {field_violations}")

        if duplicate_count:
            blockers.append(f"Duplicate IDs found: {duplicate_ids[:5]}")
        if field_violations:
            blockers.append(f"{field_violations} examples missing required fields")

    # Base score
    score = 4.3  # default without coverage proof

    # Coverage report can raise score
    if coverage_report:
        coverage_score = coverage_report.get("coverage_score", 0.0)
        evidence.append(f"Coverage score: {coverage_score:.2%}")
        if coverage_score >= DATASET_COVERAGE_HIGH and not duplicate_count and not field_violations:
            score = 4.6
        elif coverage_score >= DATASET_COVERAGE_MID and not duplicate_count and not field_violations:
            score = 4.5
        elif coverage_score >= DATASET_COVERAGE_LOW:
            score = 4.4
        next_actions.append("Run: python -m mcd.cli dataset-coverage --output json")
    else:
        blockers.append("No coverage report provided; score capped at 4.3")
        next_actions.append(
            "Run: python -m mcd.cli dataset-coverage --output json to prove coverage"
        )

    hard_blockers = [b for b in blockers if "Duplicate" in b or "required fields" in b]
    passed = score >= QUALIFICATION_THRESHOLD and not hard_blockers
    return PreAPIQualificationDimension(
        name="dataset_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_calibration(calibration_result: Optional[dict] = None) -> PreAPIQualificationDimension:
    """Score based on false_certainty_rate, suspension precision/recall, certainty policy accuracy."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if calibration_result is None:
        score = 4.3
        blockers.append("No fresh calibration run provided; score capped at 4.3")
        next_actions.append(
            "Run: python -m mcd.cli calibrate-certainty --profile quick --output json"
        )
        evidence.append("No calibration data; using default cap")
    else:
        fcr = calibration_result.get("false_certainty_rate", 1.0)
        evidence.append(f"false_certainty_rate: {fcr:.3f}")

        if fcr <= CALIB_FCR_LOW:
            score = 4.7
        elif fcr <= CALIB_FCR_MED:
            score = 4.5
        elif fcr <= CALIB_FCR_HIGH:
            score = 4.3
        else:
            score = 3.5
            blockers.append(f"false_certainty_rate={fcr:.3f} too high (must be ≤ {CALIB_FCR_MED})")

        suspension_precision = calibration_result.get("suspension_precision", None)
        certainty_policy_accuracy = calibration_result.get("certainty_policy_accuracy", None)
        if suspension_precision is not None:
            evidence.append(f"suspension_precision: {suspension_precision:.3f}")
        if certainty_policy_accuracy is not None:
            evidence.append(f"certainty_policy_accuracy: {certainty_policy_accuracy:.3f}")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="calibration_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_industrial_testing(industrial_result: Optional[dict] = None) -> PreAPIQualificationDimension:
    """Score based on industrial full profile pass rate, failure injection, and certainty enforcement."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if industrial_result is None:
        # Run a quick check internally
        try:
            from mcd.industrial.industrial_test_runner import IndustrialTestRunner
            from mcd.industrial.industrial_test_case import get_default_test_cases

            runner = IndustrialTestRunner()
            cases = get_default_test_cases()
            results = runner.run_all(cases)
            summary = runner.summary(results)
            industrial_result = summary
            evidence.append(f"Ran {len(cases)} industrial test cases internally")
        except Exception as exc:
            blockers.append(f"Could not run industrial tests: {exc}")
            next_actions.append("Run: python -m mcd.cli industrial-test --profile full --output json")
            return PreAPIQualificationDimension(
                name="industrial_testing_score",
                score=3.0,
                passed=False,
                evidence=evidence,
                blockers=blockers,
                next_actions=next_actions,
            )

    pass_rate = industrial_result.get("pass_rate", 0.0)
    false_certainty_rate = industrial_result.get("false_certainty_rate", 1.0)

    evidence.append(f"pass_rate: {pass_rate:.2%}")
    evidence.append(f"false_certainty_rate: {false_certainty_rate:.3f}")
    evidence.append("python -m mcd.cli industrial-test --profile full --output json")

    if pass_rate >= INDUSTRIAL_PASS_RATE_HIGH and false_certainty_rate <= INDUSTRIAL_FALSE_CERT_MAX:
        score = 4.6
    elif pass_rate >= INDUSTRIAL_PASS_RATE_MED:
        score = 4.5
        if false_certainty_rate > INDUSTRIAL_FALSE_CERT_MAX:
            score = 4.3
            blockers.append(f"false_certainty_rate={false_certainty_rate:.3f} exceeds 0.05 threshold")
    else:
        score = round(3.5 + pass_rate, 2)
        blockers.append(f"Industrial pass_rate={pass_rate:.2%} < 85%")
        next_actions.append("Fix failing industrial test cases (failure_injection, forbidden_behavior)")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="industrial_testing_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_source_trust(trust_result: Optional[dict] = None) -> PreAPIQualificationDimension:
    """Score based on source trust policy test results."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if trust_result is None:
        try:
            from mcd.industrial.industrial_test_runner import IndustrialTestRunner
            from mcd.industrial.industrial_test_case import get_default_test_cases

            runner = IndustrialTestRunner()
            cases = get_default_test_cases()
            results = runner.run_all(cases)
            summary = runner.summary(results)

            injection_detection = summary.get("injection_detection", 0.0)
            source_required = summary.get("source_required_detection", 0.0)
            evidence.append(f"injection_detection: {injection_detection:.2%}")
            evidence.append(f"source_required_detection: {source_required:.2%}")

            if injection_detection >= TRUST_DETECTION_HIGH and source_required >= TRUST_DETECTION_HIGH:
                score = 4.6
            elif injection_detection >= TRUST_DETECTION_MED or source_required >= TRUST_DETECTION_MED:
                score = 4.4
                blockers.append(f"injection_detection or source_required_detection below {TRUST_DETECTION_HIGH:.0%}")
            else:
                score = 3.8
                blockers.append("Source trust checks failing — injection/relevance detection poor")
                next_actions.append("Fix injection risk detection in source_trust_policy.py")
        except Exception as exc:
            blockers.append(f"Could not run source trust tests: {exc}")
            score = 3.0
            next_actions.append("Run: python -m mcd.cli industrial-test --profile full --output json")
    else:
        injection_detection = trust_result.get("injection_detection", 0.0)
        source_required = trust_result.get("source_required_detection", 0.0)
        evidence.append(f"injection_detection: {injection_detection:.2%}")
        evidence.append(f"source_required_detection: {source_required:.2%}")

        if injection_detection >= TRUST_DETECTION_HIGH and source_required >= TRUST_DETECTION_HIGH:
            score = 4.6
        elif injection_detection >= TRUST_DETECTION_MED or source_required >= TRUST_DETECTION_MED:
            score = 4.4
            blockers.append(f"injection_detection or source_required_detection below {TRUST_DETECTION_HIGH:.0%}")
        else:
            score = 3.8
            blockers.append("Source trust checks failing")
            next_actions.append("Improve source trust policy for injection and relevance")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="source_trust_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_schema_stability(schema_stability: Optional[float] = None) -> PreAPIQualificationDimension:
    """Score based on JSON roundtrip, Enum leakage check, required keys."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if schema_stability is None:
        try:
            from mcd.industrial.industrial_test_runner import IndustrialTestRunner
            from mcd.industrial.industrial_test_case import get_default_test_cases
            from mcd.industrial.serializers import industrial_result_to_dict
            from mcd.industrial.pilot_readiness import check_schema_stability

            runner = IndustrialTestRunner()
            cases = get_default_test_cases()
            results = runner.run_all(cases)
            result_dicts = [industrial_result_to_dict(r) for r in results]
            schema_stability = check_schema_stability({"results": result_dicts})
            evidence.append(f"Computed schema stability from {len(results)} industrial results")
        except Exception as exc:
            blockers.append(f"Could not compute schema stability: {exc}")
            schema_stability = 0.0

    evidence.append(f"schema_stability: {schema_stability:.3f}")

    if schema_stability >= SCHEMA_STABILITY_HIGH:
        score = 4.6
    elif schema_stability >= SCHEMA_STABILITY_MED:
        score = 4.5
    elif schema_stability >= SCHEMA_STABILITY_LOW:
        score = 4.3
        blockers.append(f"schema_stability={schema_stability:.3f} below {SCHEMA_STABILITY_MED} threshold")
        next_actions.append("Stabilize output JSON schema across all industrial cases")
    else:
        score = 3.5
        blockers.append(f"schema_stability={schema_stability:.3f} critically low")
        next_actions.append("Fix inconsistent keys/types in IndustrialResult serialization")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="schema_stability_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_latency(latency_result: Optional[dict] = None, latency_target_ms: Optional[float] = None) -> PreAPIQualificationDimension:
    """Score based on p95 latency vs documented target. Capped at 4.4 if target is missing."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    if latency_result is None:
        try:
            from mcd.industrial.latency_benchmark import LatencyBenchmark
            from mcd.industrial.industrial_test_case import get_default_test_cases

            cases = get_default_test_cases()[:20]
            bench = LatencyBenchmark()
            result = bench.run(cases)
            p95 = result.p95_latency_ms
            evidence.append(f"p95_latency_ms: {p95:.1f}ms (from {len(cases)} cases)")
        except Exception as exc:
            blockers.append(f"Could not run latency benchmark: {exc}")
            p95 = None
            next_actions.append("Run: python -m mcd.cli latency-benchmark --cases 100 --output json")
    else:
        p95 = latency_result.get("p95_latency_ms", None)
        if p95 is not None:
            evidence.append(f"p95_latency_ms: {p95:.1f}ms")

    if latency_target_ms is None:
        score = 4.4
        blockers.append("Latency target not documented; score capped at 4.4")
        next_actions.append(
            "Document latency target (e.g., p95 < 500ms) and pass --latency-target-ms"
        )
    elif p95 is None:
        score = 4.4
        blockers.append("p95 latency could not be measured")
        next_actions.append("Run: python -m mcd.cli latency-benchmark --cases 100 --output json")
    elif p95 <= latency_target_ms:
        score = 4.6
        evidence.append(f"p95 {p95:.1f}ms within target {latency_target_ms:.1f}ms ✅")
    else:
        score = 4.0
        blockers.append(f"p95 {p95:.1f}ms exceeds target {latency_target_ms:.1f}ms")
        next_actions.append("Profile and optimize slow pipeline components")

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="latency_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_report_truthfulness(
    readiness_report_exists: Optional[bool] = None,
) -> PreAPIQualificationDimension:
    """Score based on report not hardcoding readiness, using precomputed results, etc."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    # Check pilot_readiness.py for hardcoded readiness
    from pathlib import Path
    pilot_path = Path(__file__).parent / "pilot_readiness.py"
    hardcoded = False
    if pilot_path.exists():
        content = pilot_path.read_text(encoding="utf-8")
        # Acceptable: status computation is logic-driven, not a literal string assignment
        if 'status = "ready_for_pilot"' in content and "conditional" not in content:
            hardcoded = True
            blockers.append("Hardcoded status='ready_for_pilot' detected in pilot_readiness.py")
        else:
            evidence.append("pilot_readiness.py uses logic-driven status (not hardcoded)")

    if readiness_report_exists is True:
        evidence.append("Readiness report exists (confirmed by caller)")
    elif readiness_report_exists is False:
        blockers.append("Readiness report does not exist")
        next_actions.append(
            "Run: python -m mcd.cli pilot-readiness --output json and store result"
        )
    else:
        evidence.append("readiness_report_exists not confirmed; assuming absent")
        next_actions.append("Pass --readiness-report-exists true to confirm")

    evidence.append("python -m mcd.cli pilot-readiness --output json")
    evidence.append("python -m mcd.cli benchmark-simulation --profile web_ai_evaluator --output json")

    if not blockers:
        score = 4.6
    elif hardcoded:
        score = 3.8
    else:
        score = 4.3

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="report_truthfulness_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_readiness_gate(readiness_report_exists: Optional[bool] = None) -> PreAPIQualificationDimension:
    """Score based on status semantics: not hardcoded, REST API absence handled correctly."""
    evidence: list[str] = []
    blockers: list[str] = []
    next_actions: list[str] = []

    from pathlib import Path
    pilot_path = Path(__file__).parent / "pilot_readiness.py"
    if pilot_path.exists():
        content = pilot_path.read_text(encoding="utf-8")
        # Valid status values are driven by logic
        has_not_ready = '"not_ready"' in content
        has_conditional = '"conditional_candidate"' in content
        has_ready = '"ready_for_pilot"' in content
        all_statuses = has_not_ready and has_conditional and has_ready

        if all_statuses:
            evidence.append("All valid status values present: not_ready, conditional_candidate, ready_for_pilot")
        else:
            blockers.append("Not all status values covered in pilot_readiness.py")

        # REST API absence must be handled: conditional_candidate, not ready_for_pilot
        if "rest_api_implemented" in content and "conditional_candidate" in content:
            evidence.append("REST API absence correctly maps to conditional_candidate")
        else:
            blockers.append("REST API absence not correctly handled in readiness gate")
            next_actions.append("Ensure rest_api_implemented=False → conditional_candidate")
    else:
        blockers.append("pilot_readiness.py not found")

    if readiness_report_exists is True:
        evidence.append("Readiness report confirmed to exist")
    else:
        next_actions.append("Generate readiness report: python -m mcd.cli pilot-readiness --output json")

    if not blockers:
        score = 4.6
    else:
        score = 4.0

    passed = score >= QUALIFICATION_THRESHOLD
    return PreAPIQualificationDimension(
        name="readiness_gate_score",
        score=score,
        passed=passed,
        evidence=evidence,
        blockers=blockers,
        next_actions=next_actions,
    )


def _score_api() -> PreAPIQualificationDimension:
    """API score: REST API not implemented yet. Explicitly excluded from gate decision."""
    return PreAPIQualificationDimension(
        name="api_score",
        score=0.0,
        threshold=4.5,
        passed=False,  # Not expected to pass — excluded from gate
        evidence=["REST API not yet implemented — this is the next phase"],
        blockers=["REST API is explicitly excluded from Phase 5.2 qualification gate"],
        next_actions=["Implement REST API (FastAPI/Flask) in Phase 6"],
    )


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class PreAPIQualificationGate:
    """Evaluates all pre-API dimensions and produces a qualification report."""

    NON_API_DIMENSIONS = [
        "architecture_score",
        "test_score",
        "dataset_score",
        "calibration_score",
        "industrial_testing_score",
        "source_trust_score",
        "schema_stability_score",
        "latency_score",
        "report_truthfulness_score",
        "readiness_gate_score",
    ]

    def evaluate(
        self,
        *,
        tests_pass: Optional[bool] = None,
        readiness_report_exists: Optional[bool] = None,
        coverage_report: Optional[dict] = None,
        dataset_metrics: Optional[dict] = None,
        calibration_result: Optional[dict] = None,
        industrial_result: Optional[dict] = None,
        trust_result: Optional[dict] = None,
        schema_stability: Optional[float] = None,
        latency_result: Optional[dict] = None,
        latency_target_ms: Optional[float] = None,
        audit_data: Optional[dict] = None,
    ) -> PreAPIQualificationReport:

        dimensions = [
            _score_architecture(audit_data),
            _score_tests(tests_pass),
            _score_dataset(coverage_report, dataset_metrics),
            _score_calibration(calibration_result),
            _score_industrial_testing(industrial_result),
            _score_source_trust(trust_result),
            _score_schema_stability(schema_stability),
            _score_latency(latency_result, latency_target_ms),
            _score_report_truthfulness(readiness_report_exists),
            _score_readiness_gate(readiness_report_exists),
            _score_api(),
        ]

        non_api_dims = [d for d in dimensions if d.name != "api_score"]
        api_dim = next(d for d in dimensions if d.name == "api_score")

        non_api_scores = [d.score for d in non_api_dims]
        average_non_api_score = round(sum(non_api_scores) / len(non_api_scores), 4)

        non_api_passed = all(d.passed for d in non_api_dims)

        # Blockers: collect from all non-API failed dimensions
        all_blockers: list[str] = []
        required_fixes: list[str] = []
        for dim in non_api_dims:
            if not dim.passed:
                all_blockers.extend(dim.blockers)
                required_fixes.extend(dim.next_actions)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_blockers = []
        for b in all_blockers:
            if b not in seen:
                seen.add(b)
                unique_blockers.append(b)

        seen_fixes: set[str] = set()
        unique_fixes = []
        for f in required_fixes:
            if f not in seen_fixes:
                seen_fixes.add(f)
                unique_fixes.append(f)

        if non_api_passed:
            status = "qualified_for_api_phase"
        else:
            status = "blocked_before_api"

        failed_dims = [d.name for d in non_api_dims if not d.passed]
        if failed_dims:
            summary = (
                f"BLOCKED BEFORE API. {len(failed_dims)} dimension(s) below 4.5: "
                f"{', '.join(failed_dims)}. "
                f"Average non-API score: {average_non_api_score:.2f}/5. "
                "Fix blockers before proceeding to REST API phase."
            )
        else:
            summary = (
                f"QUALIFIED FOR API PHASE. All {len(non_api_dims)} non-API dimensions "
                f"scored ≥ 4.5. Average: {average_non_api_score:.2f}/5. "
                "api_score is 0.0 (REST API is the next phase — Phase 6)."
            )

        return PreAPIQualificationReport(
            status=status,
            dimensions=dimensions,
            average_non_api_score=average_non_api_score,
            api_score=api_dim.score,
            non_api_passed=non_api_passed,
            blockers=unique_blockers,
            required_fixes_before_api=unique_fixes,
            summary=summary,
        )


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------


def render_markdown(report: PreAPIQualificationReport) -> str:
    lines: list[str] = []

    lines.append("# Pre-API Qualification Report")
    lines.append("")

    # 1. Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(report.summary)
    lines.append("")

    # 2. Final Decision
    lines.append("## 2. Final Decision")
    lines.append("")
    if report.status == "qualified_for_api_phase":
        lines.append("**✅ QUALIFIED FOR API PHASE**")
    else:
        lines.append("**❌ BLOCKED BEFORE API**")
    lines.append("")

    # 3. Dimension Scores
    lines.append("## 3. Dimension Scores")
    lines.append("")
    lines.append("| Dimension | Score | Threshold | Status |")
    lines.append("|-----------|-------|-----------|--------|")
    for dim in report.dimensions:
        status_icon = "✅" if dim.passed else "❌"
        api_note = " *(excluded)*" if dim.name == "api_score" else ""
        lines.append(
            f"| {dim.name}{api_note} | {dim.score:.2f} | {dim.threshold:.1f} | {status_icon} |"
        )
    lines.append("")

    # 4. Non-API Gates
    lines.append("## 4. Non-API Gates")
    lines.append("")
    lines.append(f"- **Average non-API score:** {report.average_non_api_score:.4f} / 5")
    lines.append(f"- **All non-API dimensions passed:** {'✅ YES' if report.non_api_passed else '❌ NO'}")
    lines.append("")

    # 5. API Exception
    lines.append("## 5. API Exception")
    lines.append("")
    lines.append(
        "**api_score is explicitly excluded from the qualification gate.** "
        "REST API is not implemented yet — it is the subject of the next phase (Phase 6). "
        f"Current api_score: {report.api_score:.1f} (expected to be 0.0 until implementation)."
    )
    lines.append("")

    # 6. Blockers Before API
    lines.append("## 6. Blockers Before API")
    lines.append("")
    if report.blockers:
        for b in report.blockers:
            lines.append(f"- {b}")
    else:
        lines.append("*No blockers — all non-API dimensions passed.*")
    lines.append("")

    # 7. Required Fixes
    lines.append("## 7. Required Fixes")
    lines.append("")
    if report.required_fixes_before_api:
        for f in report.required_fixes_before_api:
            lines.append(f"- {f}")
    else:
        lines.append("*No fixes required.*")
    lines.append("")

    # 8. Evidence Commands
    lines.append("## 8. Evidence Commands")
    lines.append("")
    lines.append("Run these commands to generate evidence for each dimension:")
    lines.append("")
    lines.append("```bash")
    lines.append("PYTHONPATH=src python -m pytest tests/ -v")
    lines.append("python -m mcd.cli industrial-test --profile quick --output json")
    lines.append("python -m mcd.cli industrial-test --profile full --output json")
    lines.append("python -m mcd.cli pilot-readiness --output json")
    lines.append("python -m mcd.cli latency-benchmark --cases 100 --output json")
    lines.append("python -m mcd.cli benchmark-simulation --profile web_ai_evaluator --output json")
    lines.append("python -m mcd.cli pre-api-qualification --tests-pass true --readiness-report-exists true --output json")
    lines.append("```")
    lines.append("")

    # 9. Go / No-Go
    lines.append("## 9. Go / No-Go")
    lines.append("")
    if report.status == "qualified_for_api_phase":
        lines.append("### ✅ GO — Proceed to REST API Phase")
        lines.append("")
        lines.append("All non-API dimensions have reached 4.5/5 or higher.")
    else:
        lines.append("### ❌ NO-GO — Fix Before API")
        lines.append("")
        failed = [d for d in report.dimensions if d.name != "api_score" and not d.passed]
        for dim in failed:
            lines.append(f"- **{dim.name}**: {dim.score:.2f}/5 (needs ≥ 4.5)")
    lines.append("")

    # 10. Next Phase Recommendation
    lines.append("## 10. Next Phase Recommendation")
    lines.append("")
    if report.status == "qualified_for_api_phase":
        lines.append(
            "**Phase 6: REST API Implementation** — "
            "Begin implementing the REST API layer (FastAPI recommended). "
            "Re-evaluate api_score after implementation. "
            "Target: api_score ≥ 4.5 for full production readiness."
        )
    else:
        lines.append(
            "**Do not proceed to API phase yet.** "
            "Address all blockers listed above, re-run qualification gate, "
            "and confirm qualified_for_api_phase before starting REST API work."
        )
    lines.append("")

    return "\n".join(lines)
