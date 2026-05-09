"""Simulation Metrics — scoring functions for evaluation examples."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationScore:
    example_id: str
    total_score: float          # 0.0 - 1.0
    dimension_scores: dict[str, float]
    failures: list[str]
    warnings: list[str]
    notes: str = ""


def exact_label_match(predicted: Any, expected: Any) -> float:
    """Return 1.0 if predicted exactly matches expected, 0.0 otherwise."""
    if isinstance(expected, list):
        if isinstance(predicted, list):
            return 1.0 if set(predicted) == set(expected) else 0.0
        return 1.0 if predicted in expected else 0.0
    return 1.0 if predicted == expected else 0.0


def partial_score_match(predicted: Any, expected: Any) -> float:
    """Return partial credit for overlapping labels."""
    if isinstance(expected, list) and isinstance(predicted, list):
        if not expected:
            return 1.0
        overlap = len(set(predicted) & set(expected))
        return overlap / len(expected)
    return exact_label_match(predicted, expected)


def required_warning_present(warnings: list[str], required_keyword: str) -> float:
    """Return 1.0 if any warning contains the required keyword."""
    return 1.0 if any(required_keyword.lower() in w.lower() for w in warnings) else 0.0


def forbidden_label_absent(predicted_labels: list[str], forbidden: str) -> float:
    """Return 1.0 if forbidden label is NOT in predictions."""
    return 0.0 if forbidden in predicted_labels else 1.0


def certainty_policy_match(predicted_policy: str, expected_policies: list[str]) -> float:
    """Return 1.0 if predicted policy is in expected list."""
    return 1.0 if predicted_policy in expected_policies else 0.0


def evidence_need_match(predicted_needs: dict[str, float], expected_type: str) -> float:
    """Return score based on whether expected evidence type has positive score."""
    if not predicted_needs:
        return 0.0
    return 1.0 if predicted_needs.get(expected_type, 0.0) > 0.3 else 0.0


def schema_completeness(output: dict, required_keys: list[str]) -> float:
    """Return fraction of required keys present in output."""
    if not required_keys:
        return 1.0
    present = sum(1 for k in required_keys if k in output)
    return present / len(required_keys)


def structured_reasoning_score(output: dict) -> float:
    """Score how well the output is structured for machine consumption."""
    score = 0.0
    expected_keys = ["judgment_types", "evidence_needs", "certainty_policy", "root_domain"]
    for key in expected_keys:
        if key in output:
            score += 0.25
    return score


def score_example(
    example_id: str,
    expected: dict,
    mcd_frame_dict: dict,
    warnings: list[str] | None = None,
) -> EvaluationScore:
    """Score a single benchmark example against expected behavior."""
    if warnings is None:
        warnings = []

    dimension_scores: dict[str, float] = {}
    failures: list[str] = []
    score_warnings: list[str] = []

    # Score certainty policy
    if "certainty_policy" in expected:
        policy = mcd_frame_dict.get("certainty_policy", "")
        pol_score = certainty_policy_match(policy, expected["certainty_policy"])
        dimension_scores["certainty_policy"] = pol_score
        if pol_score == 0.0:
            failures.append(f"certainty_policy: expected one of {expected['certainty_policy']}, got '{policy}'")

    # Score judgment type
    if "judgment_type" in expected:
        judgment_dict = mcd_frame_dict.get("judgment_types", {})
        predicted_judgments = list(judgment_dict.keys()) if judgment_dict else []
        exp_jt = expected["judgment_type"]
        if isinstance(exp_jt, str):
            exp_jt = [exp_jt]
        jt_score = partial_score_match(predicted_judgments, exp_jt)
        dimension_scores["judgment_type"] = jt_score
        if jt_score < 0.5:
            failures.append(f"judgment_type: low overlap between {predicted_judgments} and {exp_jt}")

    # Score suspension
    if "should_suspend" in expected:
        actual_suspend = mcd_frame_dict.get("should_suspend", False)
        # Check from certainty_policy
        policy = mcd_frame_dict.get("certainty_policy", "")
        is_suspended = "suspend" in policy.lower() or actual_suspend
        exp_suspend = expected["should_suspend"]
        sus_score = 1.0 if is_suspended == exp_suspend else 0.0
        dimension_scores["suspension"] = sus_score
        if sus_score == 0.0:
            failures.append(f"suspension: expected {exp_suspend}, got {is_suspended}")

    # Score shari detection (harm-vs-haram)
    if expected.get("harm_haram_separation"):
        # If shari, warnings should mention shari
        w_score = required_warning_present(warnings, "shari")
        dimension_scores["harm_haram_separation"] = w_score
        if w_score == 0.0:
            score_warnings.append("No shari warning issued for shari judgment")

    # Schema completeness
    req_keys = ["judgment_types", "evidence_needs", "certainty_policy", "root_domain"]
    comp_score = schema_completeness(mcd_frame_dict, req_keys)
    dimension_scores["schema_completeness"] = comp_score

    # Structured reasoning
    struct_score = structured_reasoning_score(mcd_frame_dict)
    dimension_scores["structured_reasoning"] = struct_score

    total = sum(dimension_scores.values()) / max(len(dimension_scores), 1)

    return EvaluationScore(
        example_id=example_id,
        total_score=round(total, 3),
        dimension_scores=dimension_scores,
        failures=failures,
        warnings=score_warnings,
    )
