from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO

_FINAL_OUTPUT_TYPES = {
    "answer",
    "certificate",
    "final_judgment",
    "governedjudgment",
    "judgment",
    "project_level_conclusion",
}
_FINAL_OUTPUT_LAYERS = {
    "governedjudgment",
    "publicjudgment",
    "projectlevelconclusion",
}
_MULTI_TRANSITION_MARKERS = ("->", "=>", ",", "|")


@dataclass(frozen=True)
class OperatorContract:
    operator_id: str
    layer_from: str
    layer_to: str
    input_type: str
    output_type: str
    missing_gate: str
    gates: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    residual_policy: list[str] = field(default_factory=list)
    forbidden_outputs: list[str] = field(default_factory=list)
    rank: str = JUDGMENT_HYPOTHESIS
    reverse_trace_required: bool = True
    tests_required: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        residuals: list[str] = []

        if not self.layer_from.strip() or not self.layer_to.strip():
            residuals.append("operator_missing_layer_mapping")

        if not self.input_type.strip() or not self.output_type.strip():
            residuals.append("operator_contract_invalid")

        if not self.missing_gate.strip():
            residuals.append("operator_missing_gate")

        if not self.gates:
            residuals.append("operator_missing_gate")

        if not self.forbidden_outputs:
            residuals.append("operator_contract_invalid")

        if not self.evidence_requirements:
            residuals.append("transition_repair_missing_evidence")

        if not self.residual_policy:
            residuals.append("operator_contract_invalid")

        if _contains_multi_transition(self.layer_from) or _contains_multi_transition(self.layer_to):
            residuals.append("operator_multi_transition_forbidden")

        if _is_final_output(self.output_type) and not _is_final_layer(self.layer_to):
            residuals.append("operator_forbidden_output")

        if self.is_certificate_capable and not self.reverse_trace_required:
            residuals.append("operator_missing_reverse_trace")

        if self.rank not in {JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE}:
            residuals.append("operator_contract_invalid")

        return list(dict.fromkeys(residuals))

    @property
    def is_certificate_capable(self) -> bool:
        return self.rank == JUDGMENT_CERTIFICATE


def _contains_multi_transition(value: str) -> bool:
    normalized = value.strip()
    return any(marker in normalized for marker in _MULTI_TRANSITION_MARKERS)


def _is_final_output(output_type: str) -> bool:
    normalized = output_type.strip().replace(" ", "").replace("_", "").lower()
    return normalized in {item.replace("_", "") for item in _FINAL_OUTPUT_TYPES}


def _is_final_layer(layer: str) -> bool:
    normalized = layer.strip().replace(" ", "").replace("_", "").lower()
    return normalized in _FINAL_OUTPUT_LAYERS
