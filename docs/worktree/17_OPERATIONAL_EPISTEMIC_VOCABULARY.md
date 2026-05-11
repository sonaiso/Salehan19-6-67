# Operational Epistemic Vocabulary

## Mandatory chain

Epistemic Zero → Attention → Distinction → Designation → Identity → Universal/Particular → Domain → Aspect/Time/Judgment Rank → Contradiction Check → Linking → Interpretation → Conception → Judgment

Governance rule: no node may issue a higher-order outcome while required prior nodes remain unresolved.

## Epistemic Zero (Z0)

- Epistemic definition: alert that a presence exists in awareness but is not yet determined as knowledge.
- Mathematical form: `Z0(x) = 1 ⇔ x ∈ Awareness ∧ x ∉ DeterminedKnowledge`.
- Programming contract: `EpistemicZero(zero_id, signal_ref, reason, awareness_present, knowledge_determined, residuals)`.
- Linguistic function: marks a present-but-unknown unit in discourse.
- Forbidden transitions: `certificate_without_proof_object`, `residual_erasure`, `silent_level_skip`.
- Residuals: `unknown_signal`, `unclassified_input`, `unlinked_presence`.

## Attention (A)

- Epistemic definition: selection of a specific epistemic zero for active processing.
- Mathematical form: `A(x) = select(x | Z0(x), salience, urgency, relevance)`.
- Programming contract: `AttentionEvent(event_id, zero_id, selected_signal, salience_score, urgency_score, relevance_score, reason, residuals)`.
- Linguistic function: promotes latent presence into explicit processing focus.
- Forbidden transitions: `distinction_without_attention`, `silent_level_skip`.
- Residuals: `low_salience_conflict`, `priority_collision`, `deferred_attention`.

## Distinction (D)

- Epistemic definition: separation of one unit from background so it can be handled as a candidate subject.
- Mathematical form: `D(x,b) = unit(x) where x is separated from background b`.
- Programming contract: `DistinctionUnit(unit_id, source_signal, raw_span, boundary, distinct_from, confidence, residuals)`.
- Linguistic function: extracts bounded tokens/phrases from continuous signal.
- Forbidden transitions: `designation_without_distinction`, `root_or_pattern_as_factual_proof`.
- Residuals: `unclear_boundary`, `overlapping_units`, `fragmented_signal`.
