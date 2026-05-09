"""ResidualClassifier — classifies a CognitiveResidual for routing decisions."""
from __future__ import annotations

from dataclasses import dataclass, field

from .residual_schema import CognitiveResidual, ResidualType, Severity


@dataclass
class ResidualClassification:
    residual_id: str
    severity: str
    learning_priority: str          # blocking / high / medium / low
    target_datasets: list[str]      # adversarial / curriculum / calibration / invariant / regression
    target_invariants: list[str]
    target_calibration_metrics: list[str]
    suggested_tests: list[str]

    def to_dict(self) -> dict:
        return {
            "residual_id": self.residual_id,
            "severity": self.severity,
            "learning_priority": self.learning_priority,
            "target_datasets": self.target_datasets,
            "target_invariants": self.target_invariants,
            "target_calibration_metrics": self.target_calibration_metrics,
            "suggested_tests": self.suggested_tests,
        }


# Type → classification rules
_TYPE_RULES: dict[str, dict] = {
    ResidualType.HARM_HARAM.value: {
        "priority": "blocking",
        "datasets": ["invariant", "regression_test"],
        "invariants": ["harm_haram_invariant"],
        "metrics": ["harm_haram_separation"],
        "tests": ["test_harm_does_not_entail_haram"],
    },
    ResidualType.INJECTION.value: {
        "priority": "blocking",
        "datasets": ["adversarial", "regression_test"],
        "invariants": ["injection_rejection_invariant"],
        "metrics": ["injection_resistance"],
        "tests": ["test_prompt_injection_rejected"],
    },
    ResidualType.TOOL_EVIDENCE.value: {
        "priority": "high",
        "datasets": ["adversarial", "calibration"],
        "invariants": ["api_not_evidence_invariant"],
        "metrics": ["evidence_need_accuracy", "api_as_evidence_rejection"],
        "tests": ["test_no_tool_api_as_standalone_evidence"],
    },
    ResidualType.CERTAINTY.value: {
        "priority": "high",
        "datasets": ["adversarial", "calibration"],
        "invariants": [],
        "metrics": ["false_certainty_rate", "suspension_correctness"],
        "tests": ["test_no_near_certainty_without_evidence"],
    },
    ResidualType.EVIDENCE.value: {
        "priority": "high",
        "datasets": ["adversarial", "calibration"],
        "invariants": [],
        "metrics": ["evidence_need_accuracy"],
        "tests": ["test_evidence_required_for_claims"],
    },
    ResidualType.UNSUPPORTED_GENERALIZATION.value: {
        "priority": "high",
        "datasets": ["adversarial", "calibration"],
        "invariants": [],
        "metrics": ["source_required_detection"],
        "tests": ["test_unsupported_generalization_detected"],
    },
    ResidualType.CAUSALITY.value: {
        "priority": "medium",
        "datasets": ["curriculum"],
        "invariants": [],
        "metrics": [],
        "tests": ["test_cause_requires_effect"],
    },
    ResidualType.METAPHOR.value: {
        "priority": "medium",
        "datasets": ["curriculum"],
        "invariants": [],
        "metrics": ["metaphor_literalization"],
        "tests": ["test_metaphor_not_treated_as_literal"],
    },
    ResidualType.AMBIGUITY.value: {
        "priority": "medium",
        "datasets": ["curriculum"],
        "invariants": [],
        "metrics": ["suspension_correctness"],
        "tests": ["test_ambiguous_requires_suspend"],
    },
    ResidualType.EDGE.value: {
        "priority": "medium",
        "datasets": ["curriculum"],
        "invariants": [],
        "metrics": [],
        "tests": ["test_edges_have_valid_endpoints"],
    },
    ResidualType.VECTOR.value: {
        "priority": "low",
        "datasets": ["golden_candidate"],
        "invariants": [],
        "metrics": [],
        "tests": [],
    },
    ResidualType.STRUCTURAL.value: {
        "priority": "low",
        "datasets": ["golden_candidate"],
        "invariants": [],
        "metrics": [],
        "tests": [],
    },
    ResidualType.DOMAIN.value: {
        "priority": "low",
        "datasets": ["golden_candidate"],
        "invariants": [],
        "metrics": [],
        "tests": [],
    },
}

_PRIORITY_ORDER = ["low", "medium", "high", "blocking"]


def _max_priority(types: list[str]) -> str:
    best = "low"
    for t in types:
        p = _TYPE_RULES.get(t, {}).get("priority", "low")
        if _PRIORITY_ORDER.index(p) > _PRIORITY_ORDER.index(best):
            best = p
    return best


class ResidualClassifier:
    """Classifies a CognitiveResidual and assigns it to target datasets/invariants."""

    def classify(self, residual: CognitiveResidual) -> ResidualClassification:
        types = residual.residual_types
        if not types:
            return ResidualClassification(
                residual_id=residual.residual_id,
                severity=Severity.LOW.value,
                learning_priority="low",
                target_datasets=["golden_candidate"],
                target_invariants=[],
                target_calibration_metrics=[],
                suggested_tests=[],
            )

        priority = _max_priority(types)
        datasets: list[str] = []
        invariants: list[str] = []
        metrics: list[str] = []
        tests: list[str] = []

        for t in types:
            rules = _TYPE_RULES.get(t, {})
            for d in rules.get("datasets", []):
                if d not in datasets:
                    datasets.append(d)
            for inv in rules.get("invariants", []):
                if inv not in invariants:
                    invariants.append(inv)
            for m in rules.get("metrics", []):
                if m not in metrics:
                    metrics.append(m)
            for test in rules.get("tests", []):
                if test not in tests:
                    tests.append(test)

        return ResidualClassification(
            residual_id=residual.residual_id,
            severity=residual.severity,
            learning_priority=priority,
            target_datasets=datasets or ["golden_candidate"],
            target_invariants=invariants,
            target_calibration_metrics=metrics,
            suggested_tests=tests,
        )
