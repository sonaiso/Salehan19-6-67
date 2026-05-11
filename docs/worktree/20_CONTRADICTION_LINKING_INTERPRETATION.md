# Contradiction, Linking, Interpretation, Conception, Judgment

## Aspect / Time / Judgment Rank (ASP)

- Epistemic definition: qualifiers controlling how and when a claim is asserted and at what epistemic rank.
- Mathematical form: `ASP(c) = {aspect(c), time(c), rank(c)}`.
- Programming contract: `AspectScope`, `TemporalScope`, `JudgmentRank` objects tied to `claim_id`.
- Linguistic function: separates potency/actuality, metaphor/literality, historical/current scope, and claim rank.
- Forbidden transitions: `contradiction_without_aspect`, `contradiction_without_time`, `contradiction_without_rank`.
- Residuals: `aspect_ambiguity`, `temporal_gap`, `rank_mismatch`.

## Non-Contradiction Check (NC)

- Epistemic definition: contradiction requires same subject/predicate/meaning/domain/time/aspect/rank between assertion and negation.
- Mathematical form: `Contradiction(P,¬P) ⇔ same_subject ∧ same_predicate ∧ same_meaning ∧ same_domain ∧ same_time ∧ same_aspect ∧ same_judgment_rank`.
- Programming contract: `ContradictionCheck` with explicit boolean gates for each sameness condition.
- Linguistic function: prevents false contradiction inflation from scope shifts.
- Forbidden transitions: `contradiction_without_domain`, `contradiction_without_scope_resolution`.
- Residuals: `partial_scope_alignment`, `predicate_drift`, `meaning_divergence`.

## Linking (L)

- Epistemic definition: creates governed relation candidates between units or with prior knowledge.
- Mathematical form: `L = β(Ui,Uj,K,Γ) → LinkCandidate`.
- Programming contract: `LinkCandidate(link_id, source_unit, target_unit, link_type, license, confidence_cap, can_raise_certainty, residuals)`.
- Linguistic function: proposes relation forms (cause, condition, implication, reference) without certifying truth.
- Forbidden transitions: `link_as_certificate`, `silent_certainty_rise`.
- Residuals: `weak_link_license`, `uncertain_directionality`, `missing_bridge`.

## Interpretation (I)

- Epistemic definition: governed alignment of signal with reality, prior knowledge, principles, and licensed links to produce bounded meaning.
- Mathematical form: `I = τ(S,R,K,L,Π,Γ)`.
- Programming contract: `InterpretationObject(interpretation_id, input_signal, reality_ref, prior_information_refs, link_candidates, first_principles_applied, global_rules_applied, meaning, scope, residuals)`.
- Linguistic function: transforms expression into scoped semantic interpretation.
- Forbidden transitions: `interpretation_without_link_candidates`, `model_output_as_evidence`.
- Residuals: `underspecified_meaning`, `evidence_gap`, `scope_uncertainty`.

## Conception (C)

- Epistemic definition: structured concept formation before final truth commitment.
- Mathematical form: `C = concept(I)`.
- Programming contract: `ConceptionObject(conception_id, interpreted_meaning, concept_type, boundaries, examples, counterexamples, residuals)`.
- Linguistic function: defines concept boundaries and usage space.
- Forbidden transitions: `conception_as_certificate`.
- Residuals: `boundary_conflict`, `counterexample_pressure`.

## Judgment (J)

- Epistemic definition: governed conclusion over a claim after subject, scope, evidence, and blockers are checked.
- Mathematical form: `J(claim) ∈ {ZERO, HYPOTHESIS, CERTIFICATE}`.
- Programming contract: `JudgmentObject(judgment_id, claim_id, final_judgment, evidence_refs, residuals, reverse_trace, proof_object, governance_gate)`.
- Linguistic function: emits epistemic status as final machine-consumable judgment.
- Forbidden transitions: `certificate_without_proof_object`, `certificate_without_governance_gate`, `certificate_without_reverse_trace`, `certificate_without_evidence`.
- Residuals: `insufficient_evidence`, `reverse_trace_gap`, `blocking_residual_present`.
