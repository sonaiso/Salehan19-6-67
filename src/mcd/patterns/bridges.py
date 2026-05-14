from __future__ import annotations

from dataclasses import dataclass

from mcd.patterns.core import ClosureJudgment, ClosureResult


@dataclass(frozen=True)
class BridgePattern:
    bridge_id: str
    source_layer: str
    target_layer: str
    source_required_judgment: str
    target_minimum_completion: str
    bridge_governor: str
    required_evidence_rank: str
    preserves: tuple[str, ...]
    residual_policy: tuple[str, ...]
    fatal_barriers: tuple[str, ...]


@dataclass(frozen=True)
class BridgeValidationResult:
    bridge_id: str
    passed: bool
    blockers: tuple[str, ...]
    residuals: tuple[str, ...]


_JUDGMENT_ORDER = {
    ClosureJudgment.ZERO.value: 0,
    ClosureJudgment.HYPOTHESIS.value: 1,
    ClosureJudgment.CERTIFICATE.value: 2,
}
_CERTIFICATE_RANK = _JUDGMENT_ORDER[ClosureJudgment.CERTIFICATE.value]


def validate_bridge(
    source_closure: ClosureResult,
    target_layer: str,
    bridge_pattern: BridgePattern,
) -> BridgeValidationResult:
    blockers: list[str] = []

    if source_closure.layer != bridge_pattern.source_layer:
        blockers.append("source_layer_mismatch")
    if target_layer != bridge_pattern.target_layer:
        blockers.append("target_layer_mismatch")

    source_rank = _JUDGMENT_ORDER[source_closure.judgment.value]
    required_rank = _JUDGMENT_ORDER.get(bridge_pattern.source_required_judgment.lower(), _CERTIFICATE_RANK)
    if source_rank < required_rank:
        blockers.append("insufficient_source_judgment")

    fatal = sorted(set(source_closure.residuals) & set(bridge_pattern.fatal_barriers))
    blockers.extend(fatal)

    return BridgeValidationResult(
        bridge_id=bridge_pattern.bridge_id,
        passed=not blockers,
        blockers=tuple(dict.fromkeys(blockers)),
        residuals=source_closure.residuals,
    )


def evaluate_global_certificate(
    local_closures: dict[str, ClosureResult],
    required_layers: tuple[str, ...],
    bridge_results: tuple[BridgeValidationResult, ...],
) -> ClosureJudgment:
    if any(layer not in local_closures for layer in required_layers):
        return ClosureJudgment.ZERO
    all_local_certified = all(
        local_closures[layer].judgment == ClosureJudgment.CERTIFICATE for layer in required_layers
    )
    bridge_required = len(required_layers) > 1
    if bridge_required and not bridge_results:
        return ClosureJudgment.HYPOTHESIS
    all_bridges = all(result.passed for result in bridge_results)
    if all_local_certified and all_bridges:
        return ClosureJudgment.CERTIFICATE
    return ClosureJudgment.HYPOTHESIS
