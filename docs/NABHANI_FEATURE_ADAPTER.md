# Nabhani Feature Adapter

## Purpose

The adapter exists to encode governed answer-birth method signals as explicit ML-ready features.
It does not issue final truth and does not replace governance gates.

## Method Mapping

The adapter maps the Nabhani thought path into features:

- reality (`has_reality`, `reality_kind`, `reality_status`, `reality_access_mode`)
- source (`has_source`, `source_type`, `source_rank`, `source_role`)
- prior information (`has_prior_information`, `prior_information_kind`, `prior_information_sufficiency`)
- linking (`has_linking`, `linking_type`, `linking_validity`)
- correspondence (`has_correspondence`, `correspondence_type`)
- evidence (`has_evidence`, `evidence_type`, `evidence_sufficiency`, `evidence_matches_claim_domain`)
- method/domain/rank (`method_type`, `judgment_domain`, `certainty_rank`, `rank_source`)
- type-domain-topic operational matrix:
  - thinking type (`thinking_type`: `surface|deep|enlightened`)
  - domain scope (`thinking_domain_scope`: `rational_general|scientific_experimental`)
  - topic (`thinking_topic`: `material|human|society|creed|legislation|renaissance|concept|general`)
  - alignment/gates (`matrix_method_alignment`, `matrix_topic_alignment`, and matrix gates for reality/sense/prior/domain/depth/enlightenment/action)
- missing/residual tracking (`missing_features`, `feature_residuals`)

These are governed thinking features, not decorative boolean labels.

## Nabhani Thinking Matrix Law

The adapter treats thinking as an operational matrix, not labels:

`thinking_type × thinking_domain_scope × thinking_topic`

Examples:
- society/renaissance topics require enlightened gate.
- scientific-experimental scope cannot be treated as directly governing worldview/shari/normative/legal judgments.
- topic/type mismatch emits residuals (e.g., `matrix_thinking_type_mismatch`) instead of silent acceptance.

## Governance Boundaries

- ML outputs remain hypothesis candidates.
- Final certificate still requires `ProofObject`, `GovernanceGate`, and `ReverseTrace`.
- Birth certificate and final certificate remain separate judgments.
- Public judgments remain only `zero | hypothesis | certificate`.

## Why This Helps ML Roadmap

These features provide controlled supervision for:

- Intent Encoder
- Method Router
- Concept Graph Generator
- Reasoning Trace Decoder
- Governed Language Decoder
- Residual Predictor
- Uncertainty Calibration

The adapter improves learnability of answer-birth conditions while preserving symbolic governance authority.

## Non-Claims

- No AGI claim.
- No consciousness claim.
- No final-truth claim from model output.
