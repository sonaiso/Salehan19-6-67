# Enlightened Governed Prediction Architecture (PR #97)

## Scope

This document defines architecture and contracts only.
It does not implement training/inference runtime and does not claim production consciousness or AGI behavior.

## Thesis

Enlightened governed prediction generates and evaluates answer-birth paths, not final language directly.

Core factorization:

```text
P(Z, Y, Jb, Jf, B, R | X)
= P(Z | X) * G(Jb, Jf, B, R | Z) * P(Y | X, Z, Jb, Jf)
```

Where:

- `X`: user request and context
- `Z`: answer-birth path
- `Y`: governed language output
- `Jb`: birth judgment
- `Jf`: final judgment
- `B`: blockers
- `R`: residuals
- `G`: symbolic governance evaluator (not neural self-certification)

Neural predictions are candidates; governance remains authoritative for certificate gating.

## Epistemic Judgment Contract

Public final judgments remain exclusively:

- `ZERO`
- `HYPOTHESIS`
- `CERTIFICATE`

No fourth final status is permitted.
`birth_judgment = CERTIFICATE` does not imply final `CERTIFICATE`.

## Universal Human Rational Core

The model uses a domain-general human-rational core:

- reality
- source
- prior information
- linking
- correspondence
- evidence
- certainty rank

This aligns with existing Nabhani feature contracts (`docs/NABHANI_FEATURE_ADAPTER.md`, `data/schemas/nabhani_features.schema.json`) and is treated here as universal rational governance signals, not a narrow personality model.
The referenced schema defines the core rational-feature contract; PR #97 extends it into the full multi-path `Z` contract.

## Path Variable Contract (`Z`)

Each candidate path must model:

- `intent_status`
- `normalized_intent`
- `has_reality`
- `reality_kind`
- `reality_ref`
- `has_source`
- `source_ref`
- `has_prior_information`
- `prior_information_refs`
- `has_linking`
- `linking_type`
- `linking_validity`
- `has_correspondence`
- `correspondence_type`
- `has_evidence`
- `evidence_type`
- `evidence_matches_claim_domain`
- `method_type`
- `thinking_style`
- `thinking_means`
- `judgment_domain`
- `certainty_rank`
- `trace_path_complete`
- `trace_evidence_complete`
- `birth_judgment`
- `final_judgment`
- `residuals`
- `blockers`

## Multi-Path Generation and Selection

Generate candidate paths:

```text
Z1, Z2, ..., Zn
```

Score each path:

```text
score(Z) =
  log Pθ(Z | X)
  + α * illumination_score(Z)
  - β * governance_violation_penalty(Z)
  - γ * residual_erasure_penalty(Z)
  - δ * domain_mismatch_penalty(Z)
```

Selection rule:

- choose highest-scoring governance-valid path
- reject any path with blocking violations

## Illumination Score Contract

Positive contributors:

- has_reality
- has_source
- has_prior_information
- has_linking
- linking_validity (valid)
- has_correspondence
- has_evidence
- evidence_matches_claim_domain
- trace_path_complete

Negative contributors:

- invalid_linking
- missing_evidence
- residual_erasure
- means_as_judgment
- fluent_language_as_proof
- scientific_method_as_worldview
- scientific_method_as_normative_judgment
- final_certificate_without_gates

Illumination score is ranking support only; it is not a certificate gate replacement.

## Mentality and Domain Governance

The model recognizes mentalities/domains without surrendering judgment authority:

- scientific mentality
- formal mentality
- linguistic mentality
- normative mentality
- legal/shari mentality
- systemic mentality
- ideological/worldview mentality

For each mentality/domain, contracts must define:

- accepted sources
- allowed methods
- allowed evidence types
- forbidden transitions
- claim domains
- certainty constraints

Domain boundaries must be preserved; cross-domain certainty escalation is blocked without matching evidence contracts.

## Architecture Pipeline Contract

```text
User Request
→ Intent Encoder
→ Reality/Source Extractor
→ Prior Information Retriever
→ Mentality Recognizer
→ Method Router
→ Human Rational Feature Predictor
→ Concept Graph Generator
→ Multi-Path Thought Birth Sampler
→ Symbolic Governance Evaluator
→ Path Selector
→ Governed Language Decoder
```

## Predictor Head Contract

Required heads:

- Intent Head
- Reality/Source Head
- Prior Information Head
- Linking Head
- Correspondence Head
- Evidence Head
- Method Router Head
- Domain Head
- Certainty Rank Head
- Residual Head
- Blocker Head
- Birth Judgment Head
- Final Judgment Candidate Head

## Constrained Language Contract

Decoder output must obey:

- hypothesis cannot use certificate language
- missing evidence must be disclosed
- ambiguous intent must preserve uncertainty
- residuals must not be erased
- birth certificate must not be phrased as final certificate
- scientific method cannot output worldview/normative certainty
- final certificate requires `proof_object_ref`, `governance_gate_passed`, and `reverse_trace_ref`

Naming convention:

- `ProofObject`, `GovernanceGate`, and `ReverseTrace` denote governance artifacts/types.
- `proof_object_ref`, `governance_gate_passed`, and `reverse_trace_ref` denote required path/output fields that reference those artifacts.

## Certificate Governance Gate

Final `CERTIFICATE` is forbidden unless all are true:

- valid `ProofObject` (claim-evidence-governance linkage is complete and traceable)
- passed `GovernanceGate`
- complete `ReverseTrace`
- evidence type matches claim domain
- no blocking residual

Otherwise judgment must remain `HYPOTHESIS` or `ZERO`.

## Contribution Contract Mapping (PR #97)

- **Affected layer:** ML architecture contracts (documentation governance layer)
- **pre/current/post:** pre = answer-birth + Nabhani feature contracts exist; current = governed multi-path prediction contract defined; post = implementation-ready architecture specification only
- **phi_in / phi_out:** phi_in = governed traces and feature contracts; phi_out = governed multi-path path specification and constrained decoder contract
- **beta role:** symbolic governance remains authoritative, neural components remain candidate generators
- **preserved invariants:** no silent promotion, no residual erasure, no certificate without gates, no domain overreach without evidence
- **blocked forbidden transitions:** root/pattern/derivative as proof, fluency as proof, means as judgment, scientific-overreach, certificate without required gates
- **possible residuals:** missing reality/source/prior/linking/correspondence/evidence, domain mismatch, unresolved ambiguity
- **certificate issuance:** possible only through governance gate; never from neural score alone
- **required governance artifacts/types:** `ProofObject`, `GovernanceGate`, and `ReverseTrace` remain required for final certificate
- **required output/path references:** `proof_object_ref`, `governance_gate_passed`, and `reverse_trace_ref` must be present for final certificate eligibility
- **compliance tests:** repository markdown link checks and governance tests remain the enforcement baseline

## Implementation Boundary

This PR #97 scope is docs/contracts only:

- no model training implementation
- no new runtime inference code
- no claim of final empirical performance

## Acceptance Alignment

- No AGI claim.
- No real consciousness claim.
- Public final judgments remain `ZERO|HYPOTHESIS|CERTIFICATE`.
- Human rational method remains domain-general.
- Birth `CERTIFICATE` remains distinct from final `CERTIFICATE`.
- Neural predictions remain hypothesis candidates until symbolic governance evaluation.
