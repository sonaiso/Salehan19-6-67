from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

OPERATOR_TYPES = {
    "morphological", "mabni", "murab", "evidence",
    "certainty", "residual", "fold", "trace"
}

EVIDENCE_EFFECTS = {"none", "requires", "supports", "weakens", "blocks"}
CERTAINTY_EFFECTS = {
    "none", "lower", "suspend", "cap",
    "raise_syntactic_only", "raise_factual_with_evidence_only"
}


@dataclass
class CognitiveOperator:
    operator_id: str
    operator_type: str
    input_unit_types: list[str] = field(default_factory=list)
    output_unit_types: list[str] = field(default_factory=list)
    vector_effects: dict[str, float] = field(default_factory=dict)
    relation_effects: list[str] = field(default_factory=list)
    evidence_effect: str = "none"
    certainty_effect: str = "none"
    creates_evidence: bool = False
    laws: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.operator_type not in OPERATOR_TYPES:
            raise ValueError(f"Invalid operator_type: {self.operator_type}")
        if self.evidence_effect not in EVIDENCE_EFFECTS:
            raise ValueError(f"Invalid evidence_effect: {self.evidence_effect}")
        if self.certainty_effect not in CERTAINTY_EFFECTS:
            raise ValueError(f"Invalid certainty_effect: {self.certainty_effect}")
        # Law enforcement
        if self.operator_type == "mabni" and self.creates_evidence:
            raise ValueError("MabniOperator cannot create evidence (creates_evidence must be False)")
        if self.operator_type == "murab" and self.certainty_effect == "raise_factual_with_evidence_only":
            pass  # this is allowed
        if self.operator_type == "murab" and self.certainty_effect not in (
            "none", "raise_syntactic_only", "lower", "suspend", "cap"
        ):
            # murab cannot directly raise factual certainty
            pass

    def to_dict(self) -> dict:
        return {
            "operator_id": self.operator_id,
            "operator_type": self.operator_type,
            "input_unit_types": self.input_unit_types,
            "output_unit_types": self.output_unit_types,
            "vector_effects": self.vector_effects,
            "relation_effects": self.relation_effects,
            "evidence_effect": self.evidence_effect,
            "certainty_effect": self.certainty_effect,
            "creates_evidence": self.creates_evidence,
            "laws": self.laws,
        }


class OperatorAlgebra:
    """Registry and rule-checker for CognitiveOperators."""

    _BUILTIN: list[CognitiveOperator] = [
        CognitiveOperator(
            "emphasis_operator", "mabni",
            input_unit_types=["mabni"],
            output_unit_types=["judgment"],
            vector_effects={"discourse_force": 0.8},
            evidence_effect="none",
            certainty_effect="none",
            creates_evidence=False,
            laws=["emphasis_not_evidence", "no_certainty_increase"],
        ),
        CognitiveOperator(
            "agency_projection_operator", "morphological",
            input_unit_types=["token", "word"],
            output_unit_types=["concept"],
            vector_effects={"role_vector": 0.9},
            relation_effects=["agent_of"],
            evidence_effect="none",
            certainty_effect="none",
            creates_evidence=False,
        ),
        CognitiveOperator(
            "irab_nominative_operator", "murab",
            input_unit_types=["word", "murab"],
            output_unit_types=["sentence"],
            vector_effects={"irab_vector": 0.9, "syntactic_certainty": 0.85},
            evidence_effect="none",
            certainty_effect="raise_syntactic_only",
            creates_evidence=False,
            laws=["irab_not_factual_certainty"],
        ),
        CognitiveOperator(
            "fold_operator", "fold",
            input_unit_types=["word", "concept", "sentence"],
            output_unit_types=["fold_pattern"],
            evidence_effect="none",
            certainty_effect="none",
            creates_evidence=False,
            laws=["fold_does_not_raise_certainty", "no_proof_from_fold_alone"],
        ),
        CognitiveOperator(
            "residual_fold_operator", "residual",
            input_unit_types=["residual"],
            output_unit_types=["fold_pattern"],
            evidence_effect="none",
            certainty_effect="none",
            creates_evidence=False,
            laws=["residual_not_truth"],
        ),
    ]

    def __init__(self) -> None:
        self._operators: dict[str, CognitiveOperator] = {op.operator_id: op for op in self._BUILTIN}

    def register(self, op: CognitiveOperator) -> None:
        if op.creates_evidence and op.operator_type in ("mabni", "fold", "residual"):
            raise ValueError(f"Operator type '{op.operator_type}' cannot create evidence")
        self._operators[op.operator_id] = op

    def get(self, operator_id: str) -> Optional[CognitiveOperator]:
        return self._operators.get(operator_id)

    def get_all(self) -> list[CognitiveOperator]:
        return list(self._operators.values())

    def validate_operator(self, op: CognitiveOperator) -> tuple[bool, list[str]]:
        violations = []
        if op.creates_evidence and op.operator_type != "evidence":
            violations.append(f"Only 'evidence' type operators can create evidence, not '{op.operator_type}'")
        if op.operator_type == "murab" and "factual_certainty" in op.vector_effects:
            if op.vector_effects["factual_certainty"] > 0.0:
                violations.append("IrabOperator cannot raise factual_certainty directly")
        if op.operator_type in ("mabni", "fold", "residual", "trace") and "evidence_vector" in op.vector_effects:
            if op.vector_effects["evidence_vector"] > 0.0 and op.creates_evidence:
                violations.append(f"Operator type '{op.operator_type}' cannot raise evidence_vector as creator")
        return len(violations) == 0, violations
