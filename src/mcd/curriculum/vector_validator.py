"""VectorValidator — validates vectors against registry dimensions."""
from __future__ import annotations

from dataclasses import dataclass, field

from .vector_space import (
    ROLE_DIMENSIONS, DOMAIN_DIMENSIONS, EVIDENCE_DIMENSIONS, CERTAINTY_DIMENSIONS,
    validate_vector_dimensions,
)


@dataclass
class VectorValidationResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    score: float = 1.0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": self.violations,
            "score": round(self.score, 4),
        }


def _make_result(violations: list[str]) -> VectorValidationResult:
    passed = len(violations) == 0
    score = max(0.0, 1.0 - 0.1 * len(violations))
    return VectorValidationResult(passed=passed, violations=violations, score=score)


def validate_role_vector(v: dict[str, float]) -> VectorValidationResult:
    return _make_result(validate_vector_dimensions(v, ROLE_DIMENSIONS))


def validate_domain_vector(v: dict[str, float]) -> VectorValidationResult:
    return _make_result(validate_vector_dimensions(v, DOMAIN_DIMENSIONS))


def validate_evidence_vector(v: dict[str, float]) -> VectorValidationResult:
    return _make_result(validate_vector_dimensions(v, EVIDENCE_DIMENSIONS))


def validate_certainty_vector(v: dict[str, float]) -> VectorValidationResult:
    return _make_result(validate_vector_dimensions(v, CERTAINTY_DIMENSIONS))
