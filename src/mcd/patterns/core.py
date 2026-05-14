from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClosureJudgment(Enum):
    ZERO = "zero"
    HYPOTHESIS = "hypothesis"
    CERTIFICATE = "certificate"


@dataclass(frozen=True)
class Pattern:
    pattern_id: str
    layer: str
    family: str
    form_slots: tuple[str, ...]
    role_slots: tuple[str, ...]
    binding_relation: str
    governor: str
    required_evidence_rank: str
    closure_function: str
    minimum_completion: str
    residual_policy: tuple[str, ...]
    fatal_barriers: tuple[str, ...]
    allowed_bridges: tuple[str, ...]
    forbidden_bridges: tuple[str, ...]
    trace_policy: str


@dataclass(frozen=True)
class MorphologicalPattern(Pattern):
    pattern_form: str
    root_slots: tuple[str, ...]
    added_letters: tuple[str, ...]
    vowel_schema: tuple[str, ...]
    operator_vector: dict[str, float]
    certainty_policy: str


@dataclass(frozen=True)
class MinimumCompletion:
    mc_id: str
    layer: str
    required_form_fields: tuple[str, ...]
    required_role_fields: tuple[str, ...]
    required_dependencies: tuple[str, ...]
    required_evidence_rank: str
    residual_policy: tuple[str, ...]
    fatal_barriers: tuple[str, ...]


@dataclass(frozen=True)
class ClosureResult:
    layer: str
    pattern_id: str
    judgment: ClosureJudgment
    chi: int
    mc_satisfied: bool
    residuals: tuple[str, ...]
    blockers: tuple[str, ...]
    trace_refs: tuple[str, ...]
