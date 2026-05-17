from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO
from mcd.fractal_learning.operator_contract import OperatorContract

_FINAL_OUTPUT_TYPES = {
    "answer",
    "certificate",
    "finalanswer",
    "final_judgment",
    "governedjudgment",
    "judgment",
    "projectconclusion",
    "project_level_conclusion",
    "projectlevelconclusion",
}
_FINAL_OUTPUT_LAYERS = {
    "governedjudgment",
    "projectlevelconclusion",
    "publicjudgment",
}
_RANK_ORDER = {
    JUDGMENT_ZERO: 0,
    JUDGMENT_HYPOTHESIS: 1,
    JUDGMENT_CERTIFICATE: 2,
}
_DEFAULT_FORBIDDEN_FINAL_OUTPUTS = [
    "Judgment",
    "Certificate",
    "FinalAnswer",
    "ProjectConclusion",
]


@dataclass(frozen=True)
class OperatorCompositionContract:
    chain_id: str
    operators: list[OperatorContract]
    layer_sequence: list[str] = field(default_factory=list)
    input_type: str = ""
    output_type: str = ""
    rank_policy: str = "weakest_link_ceiling"
    residual_policy: list[str] = field(default_factory=lambda: ["union_non_erasing"])
    forbidden_final_outputs: list[str] = field(default_factory=lambda: list(_DEFAULT_FORBIDDEN_FINAL_OUTPUTS))
    required_trace_composition: bool = True


@dataclass
class OperatorChainCandidate:
    contract: OperatorCompositionContract
    emitted_residuals: list[str] = field(default_factory=list)
    composed_trace: list[str] = field(default_factory=list)
    requested_rank: str | None = None
    chain_residuals: list[str] | None = None


@dataclass(frozen=True)
class ChainValidationResult:
    accepted: bool
    residuals: list[str] = field(default_factory=list)
    rank: str = JUDGMENT_ZERO
    output_type: str = ""
    chain_residuals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompositionRegistrationResult:
    accepted: bool
    residuals: list[str] = field(default_factory=list)
    rank: str = JUDGMENT_ZERO
    output_type: str = ""
    chain_residuals: list[str] = field(default_factory=list)


class FractalOperatorCompositionRegistry:
    def __init__(self) -> None:
        self._contracts: dict[str, OperatorCompositionContract] = {}

    def register(self, candidate: OperatorChainCandidate) -> CompositionRegistrationResult:
        result = validate_operator_chain(candidate)
        if not result.accepted:
            return CompositionRegistrationResult(
                accepted=False,
                residuals=result.residuals,
                rank=result.rank,
                output_type=result.output_type,
                chain_residuals=result.chain_residuals,
            )
        self._contracts[candidate.contract.chain_id] = candidate.contract
        return CompositionRegistrationResult(
            accepted=True,
            residuals=[],
            rank=result.rank,
            output_type=result.output_type,
            chain_residuals=result.chain_residuals,
        )

    def get(self, chain_id: str) -> OperatorCompositionContract | None:
        return self._contracts.get(chain_id)


def validate_operator_chain(candidate: OperatorChainCandidate) -> ChainValidationResult:
    contract = candidate.contract
    operators = list(contract.operators)
    residuals: list[str] = []

    if not operators:
        residuals.append("operator_chain_invalid")
        return ChainValidationResult(accepted=False, residuals=residuals, rank=JUDGMENT_ZERO)

    for operator in operators:
        if operator.validate():
            residuals.append("operator_chain_invalid")
            break

    for previous, current in zip(operators, operators[1:]):
        if previous.layer_to != current.layer_from:
            residuals.append("operator_chain_layer_mismatch")
        if previous.output_type != current.input_type:
            residuals.append("operator_chain_type_mismatch")

    if contract.layer_sequence:
        if contract.layer_sequence[0] != operators[0].layer_from:
            residuals.append("operator_chain_layer_mismatch")
        if contract.layer_sequence[-1] != operators[-1].layer_to:
            residuals.append("operator_chain_layer_mismatch")

    final_operator = operators[-1]
    chain_input = contract.input_type or operators[0].input_type
    chain_output = contract.output_type or final_operator.output_type
    if chain_input != operators[0].input_type or chain_output != final_operator.output_type:
        residuals.append("operator_chain_type_mismatch")

    if _is_forbidden_final_output(chain_output, contract.forbidden_final_outputs) and not _is_final_layer(final_operator.layer_to):
        residuals.append("operator_chain_forbidden_final_output")

    weakest_rank = min((operator.rank for operator in operators), key=_rank_value)
    rank = weakest_rank
    if candidate.requested_rank:
        if _rank_value(candidate.requested_rank) > _rank_value(weakest_rank):
            residuals.append("operator_chain_rank_overclaim")
        else:
            rank = candidate.requested_rank

    policy_residuals = set(candidate.emitted_residuals)
    for operator in operators:
        policy_residuals.update(operator.residual_policy)
    aggregated_residuals = sorted(policy_residuals)

    if candidate.chain_residuals is not None:
        declared = set(candidate.chain_residuals)
        if not policy_residuals.issubset(declared):
            residuals.append("operator_chain_residual_erasure")
        aggregated_residuals = sorted(declared.union(policy_residuals))

    if contract.required_trace_composition and not candidate.composed_trace:
        residuals.append("operator_chain_missing_trace_composition")

    if any(operator.is_certificate_capable for operator in operators) and not candidate.composed_trace:
        residuals.append("operator_chain_missing_trace_composition")

    residuals = list(dict.fromkeys(residuals))
    return ChainValidationResult(
        accepted=not residuals,
        residuals=residuals,
        rank=rank,
        output_type=chain_output,
        chain_residuals=aggregated_residuals,
    )


def _normalize(value: str) -> str:
    return value.strip().replace(" ", "").replace("_", "").lower()


def _is_forbidden_final_output(output_type: str, forbidden_outputs: list[str]) -> bool:
    normalized_output = _normalize(output_type)
    forbidden = {_normalize(item) for item in forbidden_outputs}
    return normalized_output in forbidden or normalized_output in {_normalize(item) for item in _FINAL_OUTPUT_TYPES}


def _is_final_layer(layer: str) -> bool:
    return _normalize(layer) in _FINAL_OUTPUT_LAYERS


def _rank_value(rank: str) -> int:
    return _RANK_ORDER.get(rank, -1)
