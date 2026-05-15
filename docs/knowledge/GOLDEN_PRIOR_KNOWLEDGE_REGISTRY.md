# GOLDEN PRIOR KNOWLEDGE REGISTRY (#107)

## GoldenPriorKnowledgeBase
GoldenPriorKnowledgeBase (GPKB) is the governed prior layer used by Fractal Governance to prevent re-discovering already-established knowledge in each run.

## Core Objects
- **PriorRule**: scoped prior statement with evidence obligations and certificate constraints.
- **PriorScope**: domain/condition boundary where a prior is valid.
- **CertaintyLevel**: epistemic strength class (`FORMAL_CERTAINTY`, `COMPUTATIONAL_CONTRACT`, `EMPIRICAL_UNDER_CONDITIONS`, `LINGUISTIC_NORMATIVE`, `CONTEXTUAL_USAGE`, `HYPOTHESIS_PRIOR`).
- **EvidenceRequirement**: minimum evidence set required before certainty ascent.
- **CertificateBlocker**: explicit blocker that forbids certificate under specific conditions.
- **ResidualExpectation**: required residuals that must be emitted/preserved.
- **ForbiddenTransition**: transition that must never be allowed.
- **ReverseTraceRequirement**: reverse trace completeness obligations.
- **PriorKnowledgeGate**: gate that evaluates case claims against PriorRules before certificate eligibility.

## Why metrics alone are insufficient
Metrics report outcomes after decisions. They do not define domain-specific constraints that must be checked before certificate ascent. Without prior rules, false certificate metrics become under-specified because blockers are not explicitly declared.

## Why prior knowledge is required for governed judgment
Governed judgment needs explicit memory of already-established constraints: scope, evidence requirements, forbidden transitions, blockers, and residual obligations. GPKB gives the court a deterministic standard for deciding whether a claim can rise.

## Why prior knowledge is not always absolute certainty
Prior knowledge includes different certainty modes. Formal mathematics can reach formal certainty under formal scope, while empirical and linguistic decisions often remain conditional and may preserve residuals.

## Certainty distinctions
- **Formal/math certainty**: proof-bound and scope-bound; certificate requires formal proof obligations.
- **Empirical certainty**: condition-bound; alternative causes or missing measurements can block certificate.
- **Linguistic/contextual certainty**: context-sensitive; ambiguity/metaphor can support strong hypotheses while residuals still block certificate.

## Link to false_certificate_rate
`false_certificate_rate` is meaningful only when certificate blockers and evidence obligations are explicitly modeled. GPKB supplies these blockers so certificate errors are measured against declared prior law rather than score signals alone.

## Governance constraints for #107
- No model training.
- No external model output collection.
- No claim of trained Fractal Governance Network.
- No artificial consciousness claim.
- Global theorem status remains `STRONG_HYPOTHESIS`.
