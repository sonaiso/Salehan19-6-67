"""Epistemic axioms extracted from Nabhani's rational method (الطريقة العقلية).

These are not legal rulings (أحكام شرعية) but epistemic rules (قواعد معرفية)
that govern how the mind produces and validates knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EpistemicAxiom:
    axiom_id: str
    name: str
    arabic_name: str
    statement: str
    domain: str
    required_inputs: List[str]
    rejects: List[str]
    gate_name: str
    certainty_policy: str


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

AXIOM_REGISTRY: Dict[str, EpistemicAxiom] = {
    "no_knowledge_without_reality": EpistemicAxiom(
        axiom_id="AX-01",
        name="no_knowledge_without_reality",
        arabic_name="لا معرفة بلا واقع",
        statement="Every genuine piece of knowledge must be anchored to a reality (واقع) — a thing, event, or state that exists or existed.",
        domain="epistemology",
        required_inputs=["target_reality"],
        rejects=["pure_imagination", "arbitrary_assertion"],
        gate_name="reality_gate",
        certainty_policy="reject_if_missing",
    ),
    "no_thought_without_sense_or_source": EpistemicAxiom(
        axiom_id="AX-02",
        name="no_thought_without_sense_or_source",
        arabic_name="لا فكر بلا حس أو مصدر",
        statement="Thought cannot arise in a vacuum; it requires sensory input or a trusted source.",
        domain="epistemology",
        required_inputs=["sense_source"],
        rejects=["sourceless_claim"],
        gate_name="source_gate",
        certainty_policy="suspend_if_missing",
    ),
    "no_understanding_without_prior": EpistemicAxiom(
        axiom_id="AX-03",
        name="no_understanding_without_prior",
        arabic_name="لا فهم بلا معلومات سابقة",
        statement="Understanding requires prior knowledge (معلومات سابقة) — the cognitive background that enables linking new input to meaning.",
        domain="epistemology",
        required_inputs=["prior_information"],
        rejects=["meaning_without_context"],
        gate_name="prior_gate",
        certainty_policy="suspend_if_missing",
    ),
    "prior_is_not_opinion": EpistemicAxiom(
        axiom_id="AX-04",
        name="prior_is_not_opinion",
        arabic_name="المعلومات السابقة ليست رأيًا سابقًا",
        statement="Prior information is accumulated factual/conceptual knowledge, not personal opinion or bias.",
        domain="epistemology",
        required_inputs=["prior_information"],
        rejects=["opinion_as_prior"],
        gate_name="prior_quality_gate",
        certainty_policy="flag_if_opinion",
    ),
    "thought_from_linking": EpistemicAxiom(
        axiom_id="AX-05",
        name="thought_from_linking",
        arabic_name="الفكر ينتج من ربط الواقع بالمعلومات",
        statement="Thought is produced by linking (ربط) the sensed reality to prior information; without linking there is no thought.",
        domain="epistemology",
        required_inputs=["target_reality", "prior_information", "relation_chain"],
        rejects=["isolated_assertion"],
        gate_name="linking_gate",
        certainty_policy="suspend_if_missing",
    ),
    "concept_not_just_meaning": EpistemicAxiom(
        axiom_id="AX-06",
        name="concept_not_just_meaning",
        arabic_name="المفهوم ليس معنى اللفظ بل معنى أُدرك له واقع",
        statement="A concept (مفهوم) is not merely the linguistic meaning of a word; it is a meaning that has been perceived to correspond to a reality.",
        domain="semantics",
        required_inputs=["grounded_reality"],
        rejects=["ungrounded_linguistic_meaning"],
        gate_name="concept_grounding_gate",
        certainty_policy="suspend_if_ungrounded",
    ),
    "thought_validity_by_correspondence": EpistemicAxiom(
        axiom_id="AX-07",
        name="thought_validity_by_correspondence",
        arabic_name="صحة الفكر بمطابقته للواقع",
        statement="The validity of a thought is determined by its correspondence (مطابقة) to reality — not by its internal consistency alone.",
        domain="epistemology",
        required_inputs=["correspondence_test"],
        rejects=["coherence_only_validation"],
        gate_name="correspondence_gate",
        certainty_policy="reject_if_contradicts_reality",
    ),
    "no_knowledge_without_evidence": EpistemicAxiom(
        axiom_id="AX-08",
        name="no_knowledge_without_evidence",
        arabic_name="لا معرفة معتبرة بلا دليل",
        statement="No knowledge claim is epistemically valid without evidence (دليل) — a basis that supports the claim beyond mere assertion.",
        domain="epistemology",
        required_inputs=["evidence"],
        rejects=["evidenceless_claim"],
        gate_name="evidence_gate",
        certainty_policy="suspend_if_missing",
    ),
    "certainty_is_degree": EpistemicAxiom(
        axiom_id="AX-09",
        name="certainty_is_degree",
        arabic_name="اليقين درجة وليس كل معرفة يقينًا",
        statement="Certainty (يقين) is a spectrum from hypothesis to near-certainty; not every piece of knowledge qualifies as certain.",
        domain="epistemology",
        required_inputs=["certainty"],
        rejects=["binary_certainty_assumption"],
        gate_name="certainty_gate",
        certainty_policy="score_required",
    ),
    "certainty_becomes_measure": EpistemicAxiom(
        axiom_id="AX-10",
        name="certainty_becomes_measure",
        arabic_name="اليقين إذا ثبت صار مقياسًا",
        statement="When certainty is established (≥ 0.85), the knowledge becomes a cognitive measure (مقياس) that can govern future reasoning.",
        domain="epistemology",
        required_inputs=["certainty"],
        rejects=["measure_without_certainty"],
        gate_name="measure_promotion_gate",
        certainty_policy="promote_at_0.85",
    ),
    "measure_governs_cognition": EpistemicAxiom(
        axiom_id="AX-11",
        name="measure_governs_cognition",
        arabic_name="المقياس يضبط العقلية والسلوك المعرفي",
        statement="An established cognitive measure (مقياس) disciplines the mind's reasoning patterns and epistemic behaviour.",
        domain="epistemology",
        required_inputs=["cognitive_measure"],
        rejects=["unmeasured_reasoning"],
        gate_name="measure_application_gate",
        certainty_policy="apply_measure",
    ),
    "reason_governs_perception": EpistemicAxiom(
        axiom_id="AX-12",
        name="reason_governs_perception",
        arabic_name="العقل حاكم في الإدراك لا في التشريع",
        statement="Reason governs perception (إدراك), categorization, and epistemic judgments; it does not issue normative-legal (تشريعي) rulings independently.",
        domain="meta-epistemology",
        required_inputs=[],
        rejects=["reason_as_lawgiver"],
        gate_name="domain_boundary_gate",
        certainty_policy="epistemic_only",
    ),
    "pre_revelation_epistemic": EpistemicAxiom(
        axiom_id="AX-13",
        name="pre_revelation_epistemic",
        arabic_name="قبل ورود الشرع يوجد حكم معرفي عقلي لا حكم تكليفي شرعي",
        statement="Before the arrival of revelation (الشرع), the mind can produce epistemic judgments (e.g. harm/benefit) but not normative-legal obligations or prohibitions.",
        domain="meta-epistemology",
        required_inputs=[],
        rejects=["shari_ruling_without_revelation"],
        gate_name="revelation_gate",
        certainty_policy="epistemic_without_revelation",
    ),
}
