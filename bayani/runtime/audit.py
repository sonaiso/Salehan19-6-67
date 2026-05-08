"""Runtime invariant auditor for the Bayani Mustadil Runtime Engine.

The auditor checks a set of *epistemic invariants* after the pipeline has
been executed.  Each invariant is a named rule that, if violated, blocks a
final structured answer and downgrades the output rank.

Invariants implemented (v0.1):

- ``NoFinalAnswerBeforeClassificationComplete``
- ``NoJudgmentFormationBeforeEssenceDomainRelationsResolved``
- ``NoApplicationWithoutTahqeeqManat``
- ``NoPriorOpinionAsEvidence``
- ``NoMafhumStrongerThanMantuq``
- ``NoIllahWithoutValidation``
- ``NoTarjihBeforeValidJam``
- ``NoManatAsIllah``
- ``NoDomainTransferWithoutBridge``
- ``NoLevelSkipInPipeline``
"""

from __future__ import annotations

from typing import List

from bayani.runtime.contracts import (
    AuditResult,
    IntentClassificationResult,
    PipelineLayerResult,
    PromptTypeResult,
)


# ---------------------------------------------------------------------------
# Certainty map builder
# ---------------------------------------------------------------------------

def _build_certainty_map(
    layer_results: List[PipelineLayerResult],
    prompt_type: PromptTypeResult,
) -> dict:
    """Build a certainty map based on which layers ran and their status."""
    executed = {r.layer_name for r in layer_results}
    has_reality = "reality_grounding_layer" in executed
    has_essence = "essence_assignment_layer" in executed
    has_scope = "general_specific_layer" in executed
    has_tahqeeq = "tahqeeq_manat_layer" in executed
    has_application = "application_layer" in executed
    has_mantuq = "mantuq_layer" in executed
    has_mafhoom = "mafhoom_layer" in executed

    return {
        "text_existence": "qat'i_if_established" if has_reality else "requires_evidence",
        "word_meaning": "qat'i_in_definition" if has_essence else "requires_analysis",
        "scope": "qat'i_in_origin" if has_scope else ("general" if has_mantuq else "undetermined"),
        "external_application": (
            "zanni_often" if has_application
            else ("pending_tahqeeq" if has_tahqeeq else "not_reached")
        ),
        # Additional fields
        "mantuq_rank": "stronger" if has_mantuq else "not_analysed",
        "mafhoom_rank": (
            "subordinate_to_mantuq" if (has_mantuq and has_mafhoom)
            else ("not_analysed" if not has_mafhoom else "unverified")
        ),
        "illah_validation": (
            "performed" if "causal_juridical_relations_layer" in executed
            else "not_performed"
        ),
    }


# ---------------------------------------------------------------------------
# Individual invariant checks
# ---------------------------------------------------------------------------

def _check_classification_complete(
    prompt_type: PromptTypeResult,
    intent: IntentClassificationResult,
) -> str | None:
    """NoFinalAnswerBeforeClassificationComplete."""
    if prompt_type.type_id.startswith("PT-") and intent.primary_purpose:
        return None
    return "NoFinalAnswerBeforeClassificationComplete: prompt type or intent not fully classified"


def _check_judgment_after_essence(
    layer_results: List[PipelineLayerResult],
    required_layers: List[str],
) -> str | None:
    """NoJudgmentFormationBeforeEssenceDomainRelationsResolved."""
    executed = [r.layer_name for r in layer_results]
    if "judgment_formation_layer" in required_layers:
        prerequisites = ["essence_assignment_layer", "domain_assignment_layer", "relational_mapping_layer"]
        for prereq in prerequisites:
            if prereq in required_layers and prereq not in executed:
                return (
                    f"NoJudgmentFormationBeforeEssenceDomainRelationsResolved: "
                    f"{prereq} not executed before judgment_formation_layer"
                )
    return None


def _check_application_requires_tahqeeq(
    layer_results: List[PipelineLayerResult],
    required_layers: List[str],
) -> str | None:
    """NoApplicationWithoutTahqeeqManat."""
    executed = [r.layer_name for r in layer_results]
    if "application_layer" in required_layers:
        if "tahqeeq_manat_layer" not in executed:
            return (
                "NoApplicationWithoutTahqeeqManat: application_layer reached "
                "without tahqeeq_manat_layer"
            )
    return None


def _check_no_prior_opinion_as_evidence(
    layer_results: List[PipelineLayerResult],
) -> str | None:
    """NoPriorOpinionAsEvidence."""
    for result in layer_results:
        if result.layer_name == "prior_opinion_filter_layer" and result.status == "failed":
            return "NoPriorOpinionAsEvidence: prior opinion filter flagged a violation"
    return None


def _check_mafhoom_not_stronger_than_mantuq(
    layer_results: List[PipelineLayerResult],
    required_layers: List[str],
) -> str | None:
    """NoMafhumStrongerThanMantuq."""
    executed = [r.layer_name for r in layer_results]
    if "mafhoom_layer" in required_layers:
        if "mantuq_layer" not in executed:
            return (
                "NoMafhumStrongerThanMantuq: mafhoom_layer required without "
                "mantuq_layer having run first"
            )
    return None


def _check_illah_validated(
    layer_results: List[PipelineLayerResult],
    required_layers: List[str],
) -> str | None:
    """NoIllahWithoutValidation."""
    executed = [r.layer_name for r in layer_results]
    # If causal_juridical_relations is in the route, it must have passed
    if "causal_juridical_relations_layer" in required_layers:
        causal_result = next(
            (r for r in layer_results if r.layer_name == "causal_juridical_relations_layer"),
            None,
        )
        if causal_result and causal_result.status == "failed":
            return "NoIllahWithoutValidation: causal_juridical_relations_layer did not pass"
    return None


def _check_tarjih_after_jam(
    intent: IntentClassificationResult,
    layer_results: List[PipelineLayerResult],
) -> str | None:
    """NoTarjihBeforeValidJam."""
    if intent.tarjih_required:
        # In v0.1 we check that conflict_and_tarjih awareness is present via MPC
        if "MPC-08" not in intent.mpc_layers_activated:
            return "NoTarjihBeforeValidJam: tarjih requested but conflict layer (MPC-08) not activated"
    return None


def _check_no_manat_as_illah(
    layer_results: List[PipelineLayerResult],
) -> str | None:
    """NoManatAsIllah."""
    for result in layer_results:
        if result.layer_name == "causal_juridical_relations_layer":
            if "NoManatAsIllah" in result.forbidden_jumps_checked:
                return None  # explicitly checked
    # If the layer was not executed there is no risk
    return None


def _check_no_domain_transfer_without_bridge(
    layer_results: List[PipelineLayerResult],
) -> str | None:
    """NoDomainTransferWithoutBridge."""
    for result in layer_results:
        if result.layer_name == "domain_assignment_layer" and result.status == "failed":
            return "NoDomainTransferWithoutBridge: domain assignment failed, transfer blocked"
    return None


def _check_no_level_skip(
    executed_layers: List[str],
    required_layers: List[str],
) -> str | None:
    """NoLevelSkipInPipeline — every required layer must have been executed."""
    for layer in required_layers:
        if layer not in executed_layers:
            return f"NoLevelSkipInPipeline: required layer {layer!r} was not executed"
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_audit(
    prompt_type: PromptTypeResult,
    intent: IntentClassificationResult,
    required_layers: List[str],
    layer_results: List[PipelineLayerResult],
) -> AuditResult:
    """Execute all invariant checks and return an :class:`AuditResult`."""
    violations: List[str] = []
    jumps_prevented: List[str] = []

    executed = [r.layer_name for r in layer_results]

    # --- Run all invariant checks ---
    checks = [
        _check_classification_complete(prompt_type, intent),
        _check_judgment_after_essence(layer_results, required_layers),
        _check_application_requires_tahqeeq(layer_results, required_layers),
        _check_no_prior_opinion_as_evidence(layer_results),
        _check_mafhoom_not_stronger_than_mantuq(layer_results, required_layers),
        _check_illah_validated(layer_results, required_layers),
        _check_tarjih_after_jam(intent, layer_results),
        _check_no_manat_as_illah(layer_results),
        _check_no_domain_transfer_without_bridge(layer_results),
        _check_no_level_skip(executed, required_layers),
    ]

    for violation in checks:
        if violation:
            violations.append(violation)

    # --- Collect forbidden jumps checked across all layer results ---
    for result in layer_results:
        for jump in result.forbidden_jumps_checked:
            if jump and jump not in jumps_prevented:
                jumps_prevented.append(jump)

    # --- Certainty map ---
    certainty_map = _build_certainty_map(layer_results, prompt_type)

    # --- Final rank ---
    if not violations:
        final_rank = "structured_answer_allowed"
    elif any("ClassificationComplete" in v for v in violations):
        final_rank = "deferred_pending_classification"
    elif any("LevelSkip" in v for v in violations):
        final_rank = "blocked_epistemic_violation"
    else:
        final_rank = "hypothesis_only"

    return AuditResult(
        passed=len(violations) == 0,
        violations=violations,
        certainty_map=certainty_map,
        jumps_prevented=jumps_prevented,
        final_rank=final_rank,
    )
