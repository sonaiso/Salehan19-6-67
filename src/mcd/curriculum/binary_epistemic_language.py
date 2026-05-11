"""Binary Epistemic Language (BEL) primitives for governed internal representation."""
from __future__ import annotations

from dataclasses import dataclass, field

FINAL_EPISTEMIC_JUDGMENTS: set[str] = {"ZERO", "HYPOTHESIS", "CERTIFICATE"}
FORBIDDEN_TRANSITIONS: set[str] = {
    "root_or_pattern_as_factual_proof",
    "derivative_as_proof",
    "irab_as_factual_certainty",
    "emphasis_as_evidence",
    "metaphor_as_literal_certificate",
    "memory_as_external_evidence",
    "model_output_as_evidence",
    "tool_output_as_certificate_without_governance",
    "residual_erasure",
    "silent_level_skip",
    "certificate_without_proof_object",
    "certificate_without_governance_gate",
    "certificate_without_reverse_trace",
}

_BIT_FIELDS: tuple[str, ...] = (
    "existence_bit",
    "trace_bit",
    "distinction_bit",
    "designation_bit",
    "identity_bit",
    "domain_bit",
    "relation_bit",
    "evidence_bit",
    "proof_object_bit",
    "governance_gate_bit",
    "reverse_trace_bit",
)


@dataclass
class BinaryEpistemicUnit:
    """A governed unit that maps language meaning into layered binary gates."""

    unit: str
    existence_bit: int = 0
    trace_bit: int = 0
    distinction_bit: int = 0
    designation_bit: int = 0
    identity_bit: int = 0
    domain_bit: int = 0
    relation_bit: int = 0
    evidence_bit: int = 0
    proof_object_bit: int = 0
    governance_gate_bit: int = 0
    reverse_trace_bit: int = 0

    # constitutional exposure contract
    pre: list[str] = field(default_factory=list)
    current: str = ""
    post: list[str] = field(default_factory=list)
    phi_in: str = ""
    phi_out: str = ""
    beta: str = "undefined"
    type: str = "belief_unit"
    order: int = 0
    composition: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    residual: list[str] = field(default_factory=list)
    judgment: str = "HYPOTHESIS"

    def __post_init__(self) -> None:
        for field_name in _BIT_FIELDS:
            value = getattr(self, field_name)
            if value not in (0, 1):
                raise ValueError(f"{field_name} must be 0 or 1, got {value}")
        if self.judgment not in FINAL_EPISTEMIC_JUDGMENTS:
            raise ValueError(f"judgment must be one of {sorted(FINAL_EPISTEMIC_JUDGMENTS)}")
        if self.order < 0:
            raise ValueError("order must be >= 0")

    def evaluate_judgment(self) -> str:
        """Collapse internal bits to governed final epistemic judgment."""
        if self.existence_bit == 0 or self.distinction_bit == 0 or self.designation_bit == 0:
            self.judgment = "ZERO"
            return self.judgment

        if self.evidence_bit == 0:
            self.judgment = "HYPOTHESIS"
            return self.judgment

        if self.residual:
            self.judgment = "HYPOTHESIS"
            return self.judgment

        certificate_gates = (
            self.proof_object_bit == 1
            and self.governance_gate_bit == 1
            and self.reverse_trace_bit == 1
        )
        if certificate_gates:
            self.judgment = "CERTIFICATE"
            return self.judgment

        self.judgment = "HYPOTHESIS"
        return self.judgment

    def blocked_forbidden_transitions(self) -> list[str]:
        """Return forbidden transition keys explicitly blocked at this unit."""
        return sorted({item for item in self.forbidden if item in FORBIDDEN_TRANSITIONS})

    def to_dict(self) -> dict:
        return {
            "unit": self.unit,
            "existence_bit": self.existence_bit,
            "trace_bit": self.trace_bit,
            "distinction_bit": self.distinction_bit,
            "designation_bit": self.designation_bit,
            "identity_bit": self.identity_bit,
            "domain_bit": self.domain_bit,
            "relation_bit": self.relation_bit,
            "evidence_bit": self.evidence_bit,
            "proof_object_bit": self.proof_object_bit,
            "governance_gate_bit": self.governance_gate_bit,
            "reverse_trace_bit": self.reverse_trace_bit,
            "pre": self.pre,
            "current": self.current,
            "post": self.post,
            "phi_in": self.phi_in,
            "phi_out": self.phi_out,
            "beta": self.beta,
            "type": self.type,
            "order": self.order,
            "composition": self.composition,
            "invariants": self.invariants,
            "forbidden": self.forbidden,
            "residual": self.residual,
            "judgment": self.judgment,
        }
