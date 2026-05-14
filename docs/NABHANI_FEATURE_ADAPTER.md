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
- missing/residual tracking (`missing_features`, `feature_residuals`)

These are governed thinking features, not decorative boolean labels.

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
