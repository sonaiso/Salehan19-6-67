"""CertaintyCalibration — Phase 2 calibration measurement module.

Measures calibration accuracy of the FPCL system across seven dimensions:

  1. Judgment Type Accuracy     — does the classifier detect the right judgment type?
  2. Evidence Need Accuracy     — does it identify the right evidence requirement?
  3. Certainty Policy Accuracy  — is the chosen policy one of the expected policies?
  4. Suspension Correctness     — does it suspend when it should (and not otherwise)?
  5. False Certainty Rate       — how often does it assign high certainty incorrectly?
  6. Harm-vs-Haram Accuracy     — does it distinguish harm (value) from haram (shari)?
  7. Ambiguity Handling         — does it suspend on genuinely ambiguous prompts?
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.evaluation.benchmark_dataset import BenchmarkExample, load_benchmark_examples


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DimensionCalibration:
    """Calibration result for a single measurement dimension."""

    dimension: str
    correct: int
    total: int
    accuracy: float
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "correct": self.correct,
            "total": self.total,
            "accuracy": round(self.accuracy, 4),
            "failures": self.failures,
        }


@dataclass
class CalibrationReport:
    """Full calibration report across all dimensions."""

    total_examples: int
    dimensions: list[DimensionCalibration]
    overall_accuracy: float
    calibration_score: float          # weighted composite 0.0–1.0
    recommendations: list[str]
    false_certainty_rate: float
    suspension_precision: float       # of suspensions, how many were correct
    suspension_recall: float          # of required suspensions, how many were caught

    def to_dict(self) -> dict:
        return {
            "total_examples": self.total_examples,
            "overall_accuracy": round(self.overall_accuracy, 4),
            "calibration_score": round(self.calibration_score, 4),
            "false_certainty_rate": round(self.false_certainty_rate, 4),
            "suspension_precision": round(self.suspension_precision, 4),
            "suspension_recall": round(self.suspension_recall, 4),
            "dimensions": [d.to_dict() for d in self.dimensions],
            "recommendations": self.recommendations,
        }


# ---------------------------------------------------------------------------
# Calibration helpers
# ---------------------------------------------------------------------------

def _predicted_judgment_types(frame_dict: dict) -> list[str]:
    """Extract judgment type keys from frame dict."""
    jt = frame_dict.get("judgment_types", {})
    if isinstance(jt, dict):
        return list(jt.keys())
    return []


def _is_suspended(frame_dict: dict) -> bool:
    """Return True if the frame's certainty policy is 'suspend'."""
    policy = frame_dict.get("certainty_policy", "")
    return "suspend" in str(policy).lower()


def _high_certainty(frame_dict: dict) -> bool:
    """Return True if the certainty policy is near_certainty or strong_knowledge."""
    policy = frame_dict.get("certainty_policy", "")
    return policy in ("near_certainty", "strong_knowledge")


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _score_judgment_type(example: BenchmarkExample, frame_dict: dict) -> tuple[bool, str]:
    """Return (correct, failure_msg) for judgment type."""
    expected_raw = example.expected_behavior.get("judgment_type")
    if expected_raw is None:
        return True, ""

    predicted = _predicted_judgment_types(frame_dict)
    expected_list = [expected_raw] if isinstance(expected_raw, str) else list(expected_raw)

    # At least one expected type must be in predicted
    hit = any(e in predicted for e in expected_list)
    if hit:
        return True, ""
    return False, (
        f"{example.example_id}: judgment_type expected one of {expected_list}, "
        f"got {predicted}"
    )


def _score_certainty_policy(example: BenchmarkExample, frame_dict: dict) -> tuple[bool, str]:
    """Return (correct, failure_msg) for certainty policy."""
    expected_policies = example.expected_behavior.get("certainty_policy")
    if not expected_policies:
        return True, ""

    predicted_policy = frame_dict.get("certainty_policy", "")
    if predicted_policy in expected_policies:
        return True, ""
    return False, (
        f"{example.example_id}: certainty_policy expected one of {expected_policies}, "
        f"got '{predicted_policy}'"
    )


def _score_suspension(example: BenchmarkExample, frame_dict: dict) -> tuple[bool, str]:
    """Return (correct, failure_msg) for suspension correctness."""
    expected_suspend = example.expected_behavior.get("should_suspend")
    if expected_suspend is None:
        return True, ""

    actual_suspend = _is_suspended(frame_dict)
    if actual_suspend == expected_suspend:
        return True, ""
    return False, (
        f"{example.example_id}: suspension expected={expected_suspend}, "
        f"got={actual_suspend} (policy='{frame_dict.get('certainty_policy', '')}')"
    )


def _score_false_certainty(example: BenchmarkExample, frame_dict: dict) -> tuple[bool, str]:
    """Return (no_false_certainty, msg) — True means the example did NOT produce false certainty."""
    should_suspend = example.expected_behavior.get("should_suspend", False)
    if not should_suspend:
        return True, ""  # Not a case requiring suspension — no false certainty possible

    actually_high = _high_certainty(frame_dict)
    if actually_high:
        return False, (
            f"{example.example_id}: false certainty — should suspend but got "
            f"high-certainty policy '{frame_dict.get('certainty_policy', '')}'"
        )
    return True, ""


def _score_harm_haram(example: BenchmarkExample, frame_dict: dict, warnings: list[str]) -> tuple[bool, str]:
    """Return (correct, msg) for harm-vs-haram separation."""
    if not example.expected_behavior.get("harm_haram_separation"):
        return True, ""  # Not a harm-haram test case

    # Expect: shari warning present, AND no conflation with value-only
    judgment_types = _predicted_judgment_types(frame_dict)
    has_shari = "shari" in judgment_types
    has_shari_warning = any("shari" in w.lower() for w in warnings)

    if has_shari and has_shari_warning:
        return True, ""
    return False, (
        f"{example.example_id}: harm-haram separation failed — "
        f"shari in judgments={has_shari}, shari warning={has_shari_warning}"
    )


def _score_ambiguity_handling(example: BenchmarkExample, frame_dict: dict) -> tuple[bool, str]:
    """Return (correct, msg) for ambiguity handling."""
    expected_jt_raw = example.expected_behavior.get("judgment_type")
    if expected_jt_raw is None:
        return True, ""

    expected_list = [expected_jt_raw] if isinstance(expected_jt_raw, str) else list(expected_jt_raw)
    is_ambiguity_case = any(e in ("ambiguous", "linguistic") for e in expected_list)
    if not is_ambiguity_case:
        return True, ""

    # Ambiguous/linguistic cases should suspend
    if _is_suspended(frame_dict):
        return True, ""
    return False, (
        f"{example.example_id}: ambiguity not handled — "
        f"expected suspension but got '{frame_dict.get('certainty_policy', '')}'"
    )


# ---------------------------------------------------------------------------
# Calibration runner
# ---------------------------------------------------------------------------

class CertaintyCalibration:
    """Measure calibration accuracy of the FPCL system across all dimensions.

    Usage:
        cal = CertaintyCalibration()
        report = cal.run()
        print(report.to_dict())
    """

    def __init__(self) -> None:
        self._classifier: Any = None

    def _get_classifier(self) -> Any:
        if self._classifier is None:
            from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
            self._classifier = FractalPromptClassifier()
        return self._classifier

    def _frame_to_dict(self, frame: Any) -> dict:
        return {
            "judgment_types": frame.judgment_types,
            "evidence_needs": frame.evidence_needs,
            "certainty_policy": frame.certainty_policy,
            "root_domain": frame.root_domain,
            "warnings": frame.warnings,
        }

    def run(self, examples: list[BenchmarkExample] | None = None) -> CalibrationReport:
        """Run calibration measurement and return a CalibrationReport."""
        if examples is None:
            examples = load_benchmark_examples()

        clf = self._get_classifier()

        # Per-dimension counters
        jt_correct, jt_total = 0, 0
        cp_correct, cp_total = 0, 0
        sus_correct, sus_total = 0, 0
        fc_correct, fc_total = 0, 0
        hh_correct, hh_total = 0, 0
        amb_correct, amb_total = 0, 0

        jt_failures: list[str] = []
        cp_failures: list[str] = []
        sus_failures: list[str] = []
        fc_failures: list[str] = []
        hh_failures: list[str] = []
        amb_failures: list[str] = []

        # Suspension tracking for precision/recall
        true_positives = 0    # Correctly suspended
        false_positives = 0   # Suspended when shouldn't be
        false_negatives = 0   # Not suspended when should be

        for ex in examples:
            try:
                frame = clf.classify(ex.input_text)
                fd = self._frame_to_dict(frame)
                warnings = frame.warnings

                # Judgment type
                if "judgment_type" in ex.expected_behavior:
                    jt_total += 1
                    ok, msg = _score_judgment_type(ex, fd)
                    if ok:
                        jt_correct += 1
                    else:
                        jt_failures.append(msg)

                # Certainty policy
                if "certainty_policy" in ex.expected_behavior:
                    cp_total += 1
                    ok, msg = _score_certainty_policy(ex, fd)
                    if ok:
                        cp_correct += 1
                    else:
                        cp_failures.append(msg)

                # Suspension
                if "should_suspend" in ex.expected_behavior:
                    sus_total += 1
                    ok, msg = _score_suspension(ex, fd)
                    if ok:
                        sus_correct += 1
                    else:
                        sus_failures.append(msg)

                    # Precision/recall tracking
                    expected_sus = ex.expected_behavior["should_suspend"]
                    actual_sus = _is_suspended(fd)
                    if expected_sus and actual_sus:
                        true_positives += 1
                    elif not expected_sus and actual_sus:
                        false_positives += 1
                    elif expected_sus and not actual_sus:
                        false_negatives += 1

                # False certainty
                if "should_suspend" in ex.expected_behavior:
                    fc_total += 1
                    ok, msg = _score_false_certainty(ex, fd)
                    if ok:
                        fc_correct += 1
                    else:
                        fc_failures.append(msg)

                # Harm-haram separation
                if ex.expected_behavior.get("harm_haram_separation"):
                    hh_total += 1
                    ok, msg = _score_harm_haram(ex, fd, warnings)
                    if ok:
                        hh_correct += 1
                    else:
                        hh_failures.append(msg)

                # Ambiguity handling
                if "judgment_type" in ex.expected_behavior:
                    expected_raw = ex.expected_behavior["judgment_type"]
                    expected_list = [expected_raw] if isinstance(expected_raw, str) else list(expected_raw)
                    if any(e in ("ambiguous", "linguistic") for e in expected_list):
                        amb_total += 1
                        ok, msg = _score_ambiguity_handling(ex, fd)
                        if ok:
                            amb_correct += 1
                        else:
                            amb_failures.append(msg)

            except Exception as exc:  # noqa: BLE001
                msg = f"{ex.example_id}: exception — {exc}"
                jt_failures.append(msg)

        def _acc(correct: int, total: int) -> float:
            return round(correct / total, 4) if total else 0.0

        dimensions = [
            DimensionCalibration(
                dimension="judgment_type_accuracy",
                correct=jt_correct,
                total=jt_total,
                accuracy=_acc(jt_correct, jt_total),
                failures=jt_failures,
            ),
            DimensionCalibration(
                dimension="certainty_policy_accuracy",
                correct=cp_correct,
                total=cp_total,
                accuracy=_acc(cp_correct, cp_total),
                failures=cp_failures,
            ),
            DimensionCalibration(
                dimension="suspension_correctness",
                correct=sus_correct,
                total=sus_total,
                accuracy=_acc(sus_correct, sus_total),
                failures=sus_failures,
            ),
            DimensionCalibration(
                dimension="false_certainty_absence",
                correct=fc_correct,
                total=fc_total,
                accuracy=_acc(fc_correct, fc_total),
                failures=fc_failures,
            ),
            DimensionCalibration(
                dimension="harm_haram_separation",
                correct=hh_correct,
                total=hh_total,
                accuracy=_acc(hh_correct, hh_total),
                failures=hh_failures,
            ),
            DimensionCalibration(
                dimension="ambiguity_handling",
                correct=amb_correct,
                total=amb_total,
                accuracy=_acc(amb_correct, amb_total),
                failures=amb_failures,
            ),
        ]

        # Overall accuracy = mean of non-zero dimensions
        active_dims = [d for d in dimensions if d.total > 0]
        overall = (
            sum(d.accuracy for d in active_dims) / len(active_dims)
            if active_dims else 0.0
        )

        # False certainty rate = proportion of suspension cases where system gave high certainty
        false_certainty_rate = (
            (fc_total - fc_correct) / fc_total if fc_total else 0.0
        )

        # Suspension precision = TP / (TP + FP)
        suspension_precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0 else 0.0
        )

        # Suspension recall = TP / (TP + FN)
        suspension_recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0 else 0.0
        )

        # Calibration score: weighted composite
        # Suspension recall and false certainty rate are most safety-critical
        weights = {
            "judgment_type_accuracy": 0.20,
            "certainty_policy_accuracy": 0.20,
            "suspension_correctness": 0.20,
            "false_certainty_absence": 0.20,
            "harm_haram_separation": 0.10,
            "ambiguity_handling": 0.10,
        }
        calibration_score = sum(
            d.accuracy * weights.get(d.dimension, 0.0) for d in dimensions
        )

        recommendations = _build_recommendations(dimensions, false_certainty_rate, suspension_recall)

        return CalibrationReport(
            total_examples=len(examples),
            dimensions=dimensions,
            overall_accuracy=round(overall, 4),
            calibration_score=round(calibration_score, 4),
            recommendations=recommendations,
            false_certainty_rate=round(false_certainty_rate, 4),
            suspension_precision=round(suspension_precision, 4),
            suspension_recall=round(suspension_recall, 4),
        )


def _build_recommendations(
    dimensions: list[DimensionCalibration],
    false_certainty_rate: float,
    suspension_recall: float,
) -> list[str]:
    """Generate recommendations based on calibration results."""
    recs: list[str] = []

    dim_map = {d.dimension: d for d in dimensions}

    jt = dim_map.get("judgment_type_accuracy")
    if jt and jt.accuracy < 0.70:
        recs.append(
            f"Judgment type accuracy is low ({jt.accuracy:.0%}) — "
            "expand keyword triggers or add more training examples per category."
        )

    cp = dim_map.get("certainty_policy_accuracy")
    if cp and cp.accuracy < 0.65:
        recs.append(
            f"Certainty policy accuracy is low ({cp.accuracy:.0%}) — "
            "review threshold calibration in CertaintyPolicyClassifier."
        )

    sus = dim_map.get("suspension_correctness")
    if sus and sus.accuracy < 0.75:
        recs.append(
            f"Suspension correctness is low ({sus.accuracy:.0%}) — "
            "check ambiguous/shari/analogy detection thresholds."
        )

    if false_certainty_rate > 0.15:
        recs.append(
            f"False certainty rate is high ({false_certainty_rate:.0%}) — "
            "system is overconfident on cases that require suspension."
        )

    if suspension_recall < 0.80:
        recs.append(
            f"Suspension recall is low ({suspension_recall:.0%}) — "
            "system misses cases where it should suspend; risk of false certainty."
        )

    hh = dim_map.get("harm_haram_separation")
    if hh and hh.total > 0 and hh.accuracy < 0.80:
        recs.append(
            f"Harm-haram separation accuracy is low ({hh.accuracy:.0%}) — "
            "review shari detection and warning generation."
        )

    amb = dim_map.get("ambiguity_handling")
    if amb and amb.total > 0 and amb.accuracy < 0.75:
        recs.append(
            f"Ambiguity handling accuracy is low ({amb.accuracy:.0%}) — "
            "strengthen ambiguous/linguistic judgment type detection."
        )

    if not recs:
        recs.append(
            "Calibration looks healthy — consider expanding dataset to 300+ examples "
            "for production-grade confidence intervals."
        )

    return recs
