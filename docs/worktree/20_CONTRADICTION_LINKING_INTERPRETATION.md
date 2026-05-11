# 20 — Contradiction, Linking, Interpretation

## Aspect, Time, Judgment Rank Preconditions
- Aspect: angle of predication (e.g. potential vs actual).
- Time: temporal validity scope.
- Judgment rank: question/hypothesis/analysis/factual claim/certificate candidate.

## Contradiction Check
- epistemic definition: contradiction requires same subject, predicate, meaning, domain, time, aspect, and judgment rank.
- mathematical form:
  `Contradiction(P,¬P) ⇔ same_subject ∧ same_predicate ∧ same_meaning ∧ same_domain ∧ same_time ∧ same_aspect ∧ same_judgment_rank`.
- programming contract: `ContradictionCheck(check_id, claim_a, claim_b, same_domain, same_time, same_aspect, same_judgment_rank, contradiction, residuals)`.
- linguistic function: distinguishes true contradiction from domain/aspect/time/rank shifts.
- forbidden transitions: `contradiction_without_domain`, `contradiction_without_time`, `contradiction_without_aspect`, `contradiction_without_judgment_rank`.
- residuals: `domain_mismatch`, `time_scope_missing`, `aspect_unresolved`, `rank_unaligned`.

## Linking
- epistemic definition: creates licensed relation candidates, not final interpretation/certification.
- mathematical form: `L=β(Ui,Uj,K,Γ)→LinkCandidate`.
- programming contract: `LinkCandidate(link_id, source_unit, target_unit, link_type, license, confidence_cap, can_raise_certainty, residuals)`.
- linguistic function: proposes relation types (reference, causality, entailment, metaphor).
- forbidden transitions: `interpretation_without_linking`, `certificate_from_link_only`.
- residuals: `unlicensed_link`, `weak_link_confidence`.

## Interpretation
- epistemic definition: aligns signal, reality, prior information, link candidates, first principles, and global rules.
- mathematical form: `I=τ(S,R,K,L,Π,Γ)`.
- programming contract: `InterpretationObject(interpretation_id, input_signal, reality_ref, prior_information_refs, link_candidates, first_principles_applied, global_rules_applied, meaning, residuals)`.
- linguistic function: stabilizes meaning under governance.
- forbidden transitions: `conception_without_interpretation`, `certificate_without_governance_gate`.
- residuals: `meaning_not_resolved`, `reality_alignment_gap`.
