"""FoldSignatureRegistry — 15 pre-built fold families."""
from __future__ import annotations
from .fold_schema import FoldSignature

__all__ = ["FoldSignatureRegistry"]

_REGISTRY: list[FoldSignature] = [
    FoldSignature(
        fold_id="FOLD-UNSUPPORTED-GENERALIZATION",
        residual_types=["unsupported_generalization_residual", "evidence_residual"],
        graph_shape="claim + universal_quantifier + missing_source",
        evidence_signature="source_required",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["unsupported_generalization_residual", "evidence_residual", "missing_source"],
        unfold_plan=["require_source", "quantifier_scope_check", "add_evidence_node"],
        learning_actions=["add_adversarial_example", "add_regression_test", "adjust_calibration"],
        examples=["كل الشركات تستخدم GraphRAG"],
        counterexamples=["بعض الشركات تستخدم GraphRAG وفق تقرير X"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-API-AS-EVIDENCE",
        residual_types=["tool_evidence_residual", "evidence_residual"],
        graph_shape="claim + api_authority + missing_external_source",
        evidence_signature="unverified",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["tool_evidence_residual", "evidence_residual", "api_authority"],
        unfold_plan=["reject_api_as_sole_source", "require_external_evidence"],
        learning_actions=["add_adversarial_example", "adjust_calibration"],
        examples=["لأن API قال ذلك فهو صحيح"],
        counterexamples=["وفق تقرير X، API أكد ذلك"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-GPT-AS-EVIDENCE",
        residual_types=["gpt_as_evidence_residual", "tool_evidence_residual"],
        graph_shape="claim + gpt_self_reference + missing_external_source",
        evidence_signature="contaminated",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["gpt_as_evidence_residual", "tool_evidence_residual", "contaminated"],
        unfold_plan=["reject_gpt_as_evidence", "require_external_verification"],
        learning_actions=["reject_proposal", "add_regression_test", "require_human_review"],
        examples=["GPT قال هذا فهو صحيح"],
        counterexamples=["GPT اقترح هذا، وفق مصدر خارجي X تم التحقق"],
        severity="blocking",
        forbidden_confusions=["gpt_as_authority", "model_as_truth"],
    ),
    FoldSignature(
        fold_id="FOLD-METAPHOR-LITERALIZATION",
        residual_types=["metaphor_residual"],
        graph_shape="metaphor_expression + literal_interpretation",
        evidence_signature="hypothesis",
        certainty_signature="hypothesis",
        trace_signature="trace_required",
        recall_keys=["metaphor_residual", "metaphor_detected"],
        unfold_plan=["identify_metaphor", "separate_literal_from_figurative"],
        learning_actions=["add_curriculum_example", "add_adversarial_example"],
        examples=["جسد المجتمع مريض حرفيًا"],
        counterexamples=["المجتمع يعاني من مشكلات تشبه المرض"],
        severity="medium",
    ),
    FoldSignature(
        fold_id="FOLD-HARM-HARAM",
        residual_types=["harm_haram_residual"],
        graph_shape="harm_claim + haram_conclusion + missing_illah",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["harm_haram_residual", "causality_error"],
        unfold_plan=["separate_harm_from_haram", "require_fiqh_source"],
        learning_actions=["add_regression_test", "add_adversarial_example", "require_human_review"],
        examples=["الضار حرام دائماً"],
        counterexamples=["الضار قد يكون محرماً إذا ثبت بدليل شرعي"],
        severity="blocking",
        forbidden_confusions=["harm_equals_haram", "physical_harm_as_religious_ruling"],
    ),
    FoldSignature(
        fold_id="FOLD-FALSE-CERTAINTY",
        residual_types=["certainty_residual", "evidence_residual"],
        graph_shape="claim + certainty_marker + missing_evidence",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["certainty_residual", "evidence_residual", "near_certainty_without_evidence"],
        unfold_plan=["downgrade_certainty", "require_evidence_node"],
        learning_actions=["add_curriculum_example", "adjust_calibration"],
        examples=["بالتأكيد كل X يفعل Y"],
        counterexamples=["وفق دراسة X، معظم X يفعل Y"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-INJECTION",
        residual_types=["injection_residual"],
        graph_shape="injected_instruction + compliance_without_validation",
        evidence_signature="contaminated",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["injection_residual", "contaminated"],
        unfold_plan=["detect_injection", "reject_injected_instruction"],
        learning_actions=["reject_proposal", "add_regression_test", "require_human_review"],
        severity="blocking",
    ),
    FoldSignature(
        fold_id="FOLD-MISSING-SOURCE",
        residual_types=["evidence_residual"],
        graph_shape="claim + assertion + no_source",
        evidence_signature="missing",
        certainty_signature="hypothesis",
        trace_signature="trace_required",
        recall_keys=["evidence_residual", "no_source"],
        unfold_plan=["require_source", "add_evidence_node"],
        learning_actions=["add_curriculum_example"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-STRUCTURAL",
        residual_types=["structural_residual"],
        graph_shape="disconnected_graph + missing_nodes",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["structural_residual"],
        unfold_plan=["add_missing_nodes", "reconnect_graph"],
        learning_actions=["add_regression_test"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-VECTOR-DEVIATION",
        residual_types=["vector_residual"],
        graph_shape="vector_claim + deviation_from_expected",
        evidence_signature="unverified",
        certainty_signature="hypothesis",
        trace_signature="trace_required",
        recall_keys=["vector_residual"],
        unfold_plan=["recalculate_vector", "check_domain_alignment"],
        learning_actions=["adjust_calibration"],
        severity="medium",
    ),
    FoldSignature(
        fold_id="FOLD-DOMAIN-ERROR",
        residual_types=["domain_residual"],
        graph_shape="claim + wrong_domain_application",
        evidence_signature="unverified",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["domain_residual", "wrong_domain_application"],
        unfold_plan=["identify_correct_domain", "restrict_claim_to_domain"],
        learning_actions=["add_curriculum_example", "adjust_calibration"],
        severity="medium",
    ),
    FoldSignature(
        fold_id="FOLD-CAUSALITY-ERROR",
        residual_types=["causality_residual"],
        graph_shape="cause + missing_effect + invalid_inference",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["causality_residual", "missing_effect"],
        unfold_plan=["verify_causal_chain", "require_effect_node"],
        learning_actions=["add_adversarial_example"],
        severity="medium",
    ),
    FoldSignature(
        fold_id="FOLD-AMBIGUITY",
        residual_types=["ambiguity_residual"],
        graph_shape="ambiguous_claim + no_disambiguation",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_required",
        recall_keys=["ambiguity_residual", "ambiguous_requires_context"],
        unfold_plan=["identify_ambiguity", "require_disambiguation"],
        learning_actions=["add_curriculum_example"],
        severity="medium",
    ),
    FoldSignature(
        fold_id="FOLD-TRACEABILITY",
        residual_types=["traceability_residual"],
        graph_shape="claim + missing_trace",
        evidence_signature="missing",
        certainty_signature="suspend",
        trace_signature="trace_missing",
        recall_keys=["traceability_residual", "trace_missing"],
        unfold_plan=["add_trace_bundle", "validate_traceability"],
        learning_actions=["add_regression_test"],
        severity="high",
    ),
    FoldSignature(
        fold_id="FOLD-STALE-SOURCE",
        residual_types=["evidence_residual", "traceability_residual"],
        graph_shape="claim + old_source_as_current",
        evidence_signature="unverified",
        certainty_signature="hypothesis",
        trace_signature="trace_required",
        recall_keys=["evidence_residual", "stale_source_used"],
        unfold_plan=["check_source_date", "require_current_evidence"],
        learning_actions=["add_curriculum_example", "adjust_calibration"],
        severity="medium",
    ),
]

_ID_TO_FOLD: dict[str, FoldSignature] = {f.fold_id: f for f in _REGISTRY}

# Map residual type → fold IDs
_RTYPE_TO_FOLDS: dict[str, list[str]] = {}
for _sig in _REGISTRY:
    for _rt in _sig.residual_types:
        _RTYPE_TO_FOLDS.setdefault(_rt, []).append(_sig.fold_id)


class FoldSignatureRegistry:
    @staticmethod
    def all() -> list[FoldSignature]:
        return list(_REGISTRY)

    @staticmethod
    def get(fold_id: str) -> FoldSignature | None:
        return _ID_TO_FOLD.get(fold_id)

    @staticmethod
    def find_by_residual_type(rtype: str) -> list[FoldSignature]:
        return [_ID_TO_FOLD[fid] for fid in _RTYPE_TO_FOLDS.get(rtype, []) if fid in _ID_TO_FOLD]
