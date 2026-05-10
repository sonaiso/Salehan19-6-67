from __future__ import annotations

from dataclasses import dataclass, field

from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit


OPERATOR_TYPES = {
    "statistical",
    "morphosemantic",
    "jamid",
    "mushtaq",
    "mabni",
    "murab",
    "evidence",
    "certainty",
    "proof",
    "fold",
    "residual",
    "identity",
    "gpt",
}


@dataclass
class CognitiveOperator:
    operator_id: str
    operator_type: str
    input_levels: list[str] = field(default_factory=list)
    output_levels: list[str] = field(default_factory=list)
    vector_effect: dict[str, float] = field(default_factory=dict)
    relation_effect: list[str] = field(default_factory=list)
    evidence_effect: str = "none"
    certainty_effect: str = "none"
    creates_evidence: bool = False
    can_issue_certificate: bool = False
    laws: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.operator_type not in OPERATOR_TYPES:
            raise ValueError(f"Invalid operator_type: {self.operator_type}")
        if self.operator_type != "evidence" and self.creates_evidence:
            raise ValueError("Only evidence operators can create evidence")
        if self.operator_type != "proof" and self.can_issue_certificate:
            raise ValueError("Only proof operators can issue certificates")

    def to_dict(self) -> dict:
        return {
            "operator_id": self.operator_id,
            "operator_type": self.operator_type,
            "input_levels": self.input_levels,
            "output_levels": self.output_levels,
            "vector_effect": self.vector_effect,
            "relation_effect": self.relation_effect,
            "evidence_effect": self.evidence_effect,
            "certainty_effect": self.certainty_effect,
            "creates_evidence": self.creates_evidence,
            "can_issue_certificate": self.can_issue_certificate,
            "laws": self.laws,
        }


class OperatorAlgebra:
    def __init__(self) -> None:
        self._operators: dict[str, CognitiveOperator] = {}
        self.register(CognitiveOperator("emphasis_operator", "mabni", laws=["operator_non_proof"]))
        self.register(CognitiveOperator("murab_operator", "murab", certainty_effect="syntactic_only"))
        self.register(CognitiveOperator("mushtaq_operator", "mushtaq"))
        self.register(CognitiveOperator("gpt_operator", "gpt"))

    def register(self, operator: CognitiveOperator) -> None:
        self._operators[operator.operator_id] = operator

    def get(self, operator_id: str) -> CognitiveOperator | None:
        return self._operators.get(operator_id)

    def get_all(self) -> list[CognitiveOperator]:
        return list(self._operators.values())

    @staticmethod
    def identity(level: str) -> CognitiveOperator:
        return CognitiveOperator(
            operator_id=f"identity_{level}",
            operator_type="identity",
            input_levels=[level],
            output_levels=[level],
            laws=["identity"],
        )

    @staticmethod
    def compose(op_a: CognitiveOperator, op_b: CognitiveOperator) -> CognitiveOperator:
        return CognitiveOperator(
            operator_id=f"compose({op_a.operator_id},{op_b.operator_id})",
            operator_type=op_b.operator_type,
            input_levels=op_a.input_levels or op_b.input_levels,
            output_levels=op_b.output_levels or op_a.output_levels,
            vector_effect={**op_a.vector_effect, **op_b.vector_effect},
            relation_effect=list(dict.fromkeys(op_a.relation_effect + op_b.relation_effect)),
            evidence_effect=op_b.evidence_effect if op_b.evidence_effect != "none" else op_a.evidence_effect,
            certainty_effect=op_b.certainty_effect if op_b.certainty_effect != "none" else op_a.certainty_effect,
            creates_evidence=op_a.creates_evidence or op_b.creates_evidence,
            can_issue_certificate=op_a.can_issue_certificate or op_b.can_issue_certificate,
            laws=list(dict.fromkeys(op_a.laws + op_b.laws)),
        )

    @classmethod
    def normalize_operator_chain(cls, chain: list[CognitiveOperator]) -> list[CognitiveOperator]:
        normalized: list[CognitiveOperator] = []
        for op in chain:
            if op.operator_type == "identity":
                continue
            if normalized and normalized[-1].operator_id == op.operator_id:
                continue
            normalized.append(op)
        return normalized

    @classmethod
    def commute(cls, op_a: CognitiveOperator, op_b: CognitiveOperator, _unit: GovernedFractalUnit | None = None) -> bool:
        return (
            op_a.vector_effect == op_b.vector_effect
            and op_a.relation_effect == op_b.relation_effect
            and op_a.evidence_effect == op_b.evidence_effect
            and op_a.certainty_effect == op_b.certainty_effect
        )

    @staticmethod
    def apply(operator: CognitiveOperator, unit: GovernedFractalUnit) -> GovernedFractalUnit:
        if operator.evidence_effect == "require":
            unit.evidence_state = "required"
        elif operator.evidence_effect == "present":
            unit.evidence_state = "present"
        if operator.certainty_effect == "suspend":
            unit.certainty_state = "suspend"
        elif operator.certainty_effect == "raise" and unit.evidence_state == "present":
            unit.certainty_state = "raised"
        unit.operators.append(operator.operator_id)
        return unit

    @classmethod
    def validate_associativity(cls, a: CognitiveOperator, b: CognitiveOperator, c: CognitiveOperator) -> bool:
        left = cls.compose(cls.compose(a, b), c)
        right = cls.compose(a, cls.compose(b, c))
        return (
            left.vector_effect == right.vector_effect
            and left.relation_effect == right.relation_effect
            and left.evidence_effect == right.evidence_effect
            and left.certainty_effect == right.certainty_effect
            and left.creates_evidence == right.creates_evidence
            and left.can_issue_certificate == right.can_issue_certificate
        )

    @staticmethod
    def validate_laws(
        operators: list[CognitiveOperator],
        evidence_state_before: str = "missing",
        evidence_state_after: str = "missing",
        certainty_before: float = 0.0,
        certainty_after: float = 0.0,
        residual_before: list[str] | None = None,
        residual_after: list[str] | None = None,
    ) -> tuple[bool, list[str]]:
        residual_before = residual_before or []
        residual_after = residual_after or []
        violations = []

        for op in operators:
            if op.operator_type != "evidence" and op.creates_evidence:
                violations.append(f"{op.operator_id}: non-evidence operator cannot create evidence")
            if op.operator_type != "proof" and op.can_issue_certificate:
                violations.append(f"{op.operator_id}: non-proof operator cannot issue certificate")

        if certainty_after > certainty_before and evidence_state_after != "present":
            violations.append("certainty cannot increase without valid evidence")

        if any(r not in residual_after for r in residual_before):
            violations.append("residuals cannot be erased without correction")

        return len(violations) == 0, violations
