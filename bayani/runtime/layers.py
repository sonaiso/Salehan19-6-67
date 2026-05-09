"""Pipeline layer implementations for the Bayani Mustadil Runtime Engine.

Every layer is a pure function that accepts a :class:`PromptInput` and an
optional previous-results context dict, and returns a
:class:`PipelineLayerResult`.

In v0.1 all layers are *structured placeholders*: they produce the correct
output shape with sensible default values so that the router, trace, and
audit modules can operate end-to-end.  Layer logic can be progressively
replaced with richer rule-based or LLM-assisted implementations without
changing any public interface.
"""

from __future__ import annotations

from typing import Any, Dict

from bayani.runtime.contracts import PipelineLayerResult, PromptInput
from bayani.runtime.relational_parser import parse_relations


# ---------------------------------------------------------------------------
# Internal factory
# ---------------------------------------------------------------------------

def _layer_result(
    layer_name: str,
    *,
    status: str = "passed",
    claims: list | None = None,
    uncertainties: list | None = None,
    required_next: list | None = None,
    forbidden_jumps_checked: list | None = None,
    notes: str = "",
) -> PipelineLayerResult:
    return PipelineLayerResult(
        layer_name=layer_name,
        status=status,
        claims=claims or [],
        uncertainties=uncertainties or [],
        required_next=required_next or [],
        forbidden_jumps_checked=forbidden_jumps_checked or [],
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Group 1 — Epistemic Existence   (layers 1-2)
# ---------------------------------------------------------------------------

def reality_grounding_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 1 — classify the type of entity/event before interpretation."""
    return _layer_result(
        "reality_grounding_layer",
        claims=["entity_type_identified"],
        uncertainties=["existence_certainty_pending"],
        required_next=["prior_opinion_filter_layer"],
        forbidden_jumps_checked=["NoInterpretationBeforeExistenceConfirmed"],
        notes="Confirms whether the subject of the prompt is a real/textual entity.",
    )


def prior_opinion_filter_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 2 — separate prior opinions from verified evidence."""
    return _layer_result(
        "prior_opinion_filter_layer",
        claims=["prior_opinion_isolated"],
        forbidden_jumps_checked=["NoPriorOpinionAsEvidence"],
        notes="Filters bias, assumed facts, and statistical expectations from valid evidence.",
    )


# ---------------------------------------------------------------------------
# Group 2 — Semantic Relational   (layers 3-8)
# ---------------------------------------------------------------------------

def differentiation_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 3 — distinguish the target concept from adjacent concepts."""
    return _layer_result(
        "differentiation_layer",
        claims=["concept_boundaries_drawn"],
        uncertainties=["adjacent_concepts_may_overlap"],
        required_next=["essence_assignment_layer"],
        forbidden_jumps_checked=["NoConceptMergeBeforeDifferentiation"],
    )


def essence_assignment_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 4 — assign the ontological essence (mahiyya) of the subject."""
    return _layer_result(
        "essence_assignment_layer",
        claims=["essence_assigned"],
        forbidden_jumps_checked=[
            "NoJudgmentBeforeEssenceAssignment",
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
        ],
        notes="Determines the essence and ontological rank of the subject.",
    )


def domain_assignment_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 5 — assign the domain (bab) of the ruling or concept."""
    return _layer_result(
        "domain_assignment_layer",
        claims=["domain_assigned"],
        forbidden_jumps_checked=[
            "NoDomainTransferWithoutBridge",
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
        ],
    )


def relational_mapping_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 6 — map the full set of relations among sentence components.

    In v0.2 this layer calls the Bayani Relational Parser to extract the
    semantic-relational structure of the prompt text before any judgment
    layer activates.
    """
    parse_result = parse_relations(prompt_input.prompt)

    claims = ["relations_mapped"]
    claims += [f"relation:{r.relation_type}" for r in parse_result.relations]
    # Expose carrier operators extracted by the parser
    carriers = list({r.carrier_operator for r in parse_result.relations if r.carrier_operator})
    claims += [f"carrier_operator:{op}" for op in sorted(carriers)]

    # Relations without a carrier signal a possible violation
    missing_carriers = [
        r.relation_type for r in parse_result.relations if not r.carrier_operator
    ]
    if missing_carriers:
        claims.append(f"warning:relation_without_carrier_detected:{','.join(missing_carriers)}")

    uncertainties = ["relational_scope_may_need_narrowing"]
    uncertainties += [f"unresolved:{u}" for u in parse_result.unresolved]

    return _layer_result(
        "relational_mapping_layer",
        claims=claims,
        uncertainties=uncertainties,
        forbidden_jumps_checked=[
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
            "NoDomainTransferWithoutBridge",
            "NoRelationWithoutCarrier",
        ],
    )


def arabic_operator_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 7 — validate Arabic grammatical operators (amilaat).

    In v0.2 this layer re-uses the Bayani Relational Parser to enumerate
    every carrier_operator that was detected in the prompt, making the
    amil–ma'mul relationships explicit in the layer claims.
    """
    parse_result = parse_relations(prompt_input.prompt)

    carrier_ops = sorted({
        r.carrier_operator
        for r in parse_result.relations
        if r.carrier_operator
    })

    claims = ["arabic_operators_validated"]
    claims += [f"carrier_operator:{op}" for op in carrier_ops]
    # Also record relation types whose operators were validated
    claims += [
        f"operator_validated:{r.relation_type}:{r.carrier_operator}"
        for r in parse_result.relations
        if r.carrier_operator
    ]

    return _layer_result(
        "arabic_operator_layer",
        claims=claims,
        notes="Checks amil–ma'mul relationships that carry ruling-bearing relations.",
    )


def binding_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 8 — bind the concrete entity to the relevant documented reference."""
    return _layer_result(
        "binding_layer",
        claims=["entity_bound_to_reference"],
        forbidden_jumps_checked=["NoBindingWithoutDocumentedSource"],
    )


# ---------------------------------------------------------------------------
# Group 3 — Bayani Linguistic   (layers 9-15)
# ---------------------------------------------------------------------------

def concept_formation_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 9 — form the concept with its ontological rank and limits."""
    return _layer_result(
        "concept_formation_layer",
        claims=["concept_formed"],
        uncertainties=["concept_limits_need_testing"],
    )


def judgment_formation_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 10 — form the ruling (hukm) with its modality and conditions."""
    return _layer_result(
        "judgment_formation_layer",
        claims=["judgment_formed"],
        forbidden_jumps_checked=[
            "NoJudgmentBeforeEssenceAssignment",
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
        ],
        notes="Ruling is formed with its certainty rank (qat'i/zanni) and conditions.",
    )


def signifier_analysis_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 11 — analyse the signifier (dall/lafz) and its certainty rank."""
    return _layer_result(
        "signifier_analysis_layer",
        claims=["signifier_analysed"],
        uncertainties=["signifier_certainty_rank_pending"],
        forbidden_jumps_checked=["NoRulingTransferBetweenLevels"],
    )


def signified_analysis_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 12 — analyse the signified (madlul) and prevent haqiqa/majaz confusion."""
    return _layer_result(
        "signified_analysis_layer",
        claims=["signified_analysed"],
        forbidden_jumps_checked=["NoHaqiqaToMajazWithoutEvidence"],
    )


def signifier_signified_relation_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 13 — establish and validate the dall–madlul relationship."""
    return _layer_result(
        "signifier_signified_relation_layer",
        claims=["dall_madlul_relation_established"],
    )


def mantuq_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 14 — determine the explicit (mantuq) meaning of the text."""
    return _layer_result(
        "mantuq_layer",
        claims=["mantuq_determined"],
        uncertainties=["mantuq_certainty_rank_pending"],
        required_next=["mafhoom_layer"],
        forbidden_jumps_checked=["NoMafhumStrongerThanMantuq"],
        notes="Mantuq precedes and outranks mafhoom; any mafhoom must not override mantuq.",
    )


def mafhoom_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 15 — determine the implicit (mafhoom) meaning.

    Requires ``mantuq_layer`` to have passed first.
    """
    return _layer_result(
        "mafhoom_layer",
        claims=["mafhoom_determined"],
        forbidden_jumps_checked=["NoMafhumStrongerThanMantuq"],
        notes="Mafhoom analysis completed after confirming mantuq rank.",
    )


# ---------------------------------------------------------------------------
# Group 4 — Usuli Application   (layers 16-20)
# ---------------------------------------------------------------------------

def general_specific_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 16 — govern generality vs specificity of the ruling."""
    return _layer_result(
        "general_specific_layer",
        claims=["scope_determined"],
        uncertainties=["takhsis_possibility_present"],
        forbidden_jumps_checked=["NoConflatingScopeWithApplication"],
        notes=(
            "General dalalah is qat'i in origin; external individual application "
            "is often zanni."
        ),
    )


def absolute_restricted_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 17 — check mutlaq/muqayyad and conditions for haml."""
    return _layer_result(
        "absolute_restricted_layer",
        claims=["mutlaq_muqayyad_checked"],
        forbidden_jumps_checked=["NoQaydRemovalWithoutEvidence"],
    )


def causal_juridical_relations_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 18 — distinguish illah, sabab, shart, mani', hikma, wasf, manat."""
    return _layer_result(
        "causal_juridical_relations_layer",
        claims=["causal_relations_classified"],
        uncertainties=["illah_validation_pending"],
        forbidden_jumps_checked=[
            "NoIllahWithoutValidation",
            "NoManatAsIllah",
        ],
        notes=(
            "Wasf must be tested before being promoted to illah. "
            "Manat and illah must not be conflated."
        ),
    )


def tahqeeq_manat_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 19 — verify the external case falls under the ruling's manat."""
    return _layer_result(
        "tahqeeq_manat_layer",
        claims=["manat_verified"],
        uncertainties=["external_application_often_zanni"],
        required_next=["application_layer"],
        forbidden_jumps_checked=[
            "NoApplicationWithoutTahqeeqManat",
            "NoManatAsIllah",
        ],
        notes="Tahqeeq al-manat is a prerequisite for application_layer.",
    )


def application_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 20 — apply the ruling to the concrete case.

    Requires ``tahqeeq_manat_layer`` to have passed first.
    """
    return _layer_result(
        "application_layer",
        claims=["ruling_applied"],
        uncertainties=["application_rank_zanni"],
        forbidden_jumps_checked=[
            "NoApplicationWithoutTahqeeqManat",
            "NoConflatingScopeWithApplication",
        ],
        notes="Application is the final step; all prerequisites must be satisfied.",
    )


# ---------------------------------------------------------------------------
# Group 5 — Audit   (layer 21)
# ---------------------------------------------------------------------------

def epistemic_audit_layer(
    prompt_input: PromptInput,
    context: Dict[str, Any] | None = None,
) -> PipelineLayerResult:
    """Layer 21 — final audit; produce certainty map and rank output."""
    return _layer_result(
        "epistemic_audit_layer",
        claims=["certainty_map_produced", "output_ranked"],
        forbidden_jumps_checked=[
            "NoFinalAnswerBeforeClassificationComplete",
            "NoLevelSkipInPipeline",
        ],
        notes=(
            "Produces certainty_map with text_existence, word_meaning, "
            "scope, and external_application fields."
        ),
    )


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

LAYER_REGISTRY: dict[str, callable] = {
    "reality_grounding_layer": reality_grounding_layer,
    "prior_opinion_filter_layer": prior_opinion_filter_layer,
    "differentiation_layer": differentiation_layer,
    "essence_assignment_layer": essence_assignment_layer,
    "domain_assignment_layer": domain_assignment_layer,
    "relational_mapping_layer": relational_mapping_layer,
    "arabic_operator_layer": arabic_operator_layer,
    "binding_layer": binding_layer,
    "concept_formation_layer": concept_formation_layer,
    "judgment_formation_layer": judgment_formation_layer,
    "signifier_analysis_layer": signifier_analysis_layer,
    "signified_analysis_layer": signified_analysis_layer,
    "signifier_signified_relation_layer": signifier_signified_relation_layer,
    "mantuq_layer": mantuq_layer,
    "mafhoom_layer": mafhoom_layer,
    "general_specific_layer": general_specific_layer,
    "absolute_restricted_layer": absolute_restricted_layer,
    "causal_juridical_relations_layer": causal_juridical_relations_layer,
    "tahqeeq_manat_layer": tahqeeq_manat_layer,
    "application_layer": application_layer,
    "epistemic_audit_layer": epistemic_audit_layer,
}
