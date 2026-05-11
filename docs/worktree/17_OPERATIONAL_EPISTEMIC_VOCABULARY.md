# 17 — Operational Epistemic Vocabulary

## Chain

Epistemic Zero → Attention → Distinction → Designation → Identity → Universal / Particular → Domain → Aspect / Time / Judgment Rank → Contradiction Check → Linking → Interpretation → Conception → Judgment

## Epistemic Zero
- epistemic definition: presence in awareness without determined knowledge.
- mathematical form: `Z0(x)=1 ⇔ x∈Awareness ∧ x∉DeterminedKnowledge`.
- programming contract: `EpistemicZero(zero_id, signal_ref, awareness_present, knowledge_determined, residuals)`.
- linguistic function: signals `unknown presence` that must be processed.
- forbidden transitions: `residual_erasure`, `silent_level_skip`.
- residuals: `unknown_signal`, `missing_prior_information`, `unlinked_presence`.

## Attention
- epistemic definition: selection of a Z0 signal for processing.
- mathematical form: `A(x)=select(x|Z0(x), salience, urgency, relevance)`.
- programming contract: `AttentionEvent(event_id, zero_id, selected_signal, salience_score, urgency_score, relevance_score, residuals)`.
- linguistic function: shifts from alert to focused inquiry.
- forbidden transitions: `attention_without_zero`, `silent_level_skip`.
- residuals: `attention_queue_overload`, `low_relevance_signal`.

## Judgment Closure Rule
- No final epistemic judgment outside: `ZERO`, `HYPOTHESIS`, `CERTIFICATE`.
- No certificate without: `ProofObject`, `GovernanceGate`, `ReverseTrace`, evidence-claim match, and no blocking residual.
