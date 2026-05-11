# 19 — Universal, Particular, Domain

## Universal
- epistemic definition: concept predicable of many instances.
- mathematical form: `Universal(U) ⇔ ∃x,y,z : U applies to x,y,z`.
- programming contract: `UniversalConcept(concept_id, label, applies_to_many, necessary_features, accidental_features, domain, residuals)`.
- linguistic function: supports category-level meaning.
- forbidden transitions: `universal_to_particular_without_applicability`.
- residuals: `overgeneralized_universal`, `missing_applicability_conditions`.

## Particular
- epistemic definition: determinate singular referent not predicable of many in the same way.
- mathematical form: `Particular(p) ⇔ ¬applies_to_many(p)`.
- programming contract: `ParticularUnit(particular_id, reference, designation_id, time_scope, place_scope, identity_unit_id, residuals)`.
- linguistic function: grounds claims in a concrete subject.
- forbidden transitions: `judgment_without_subject`.
- residuals: `unresolved_particular_reference`, `missing_context_scope`.

## Domain
- epistemic definition: scope in which interpretation/evidence/judgment are valid.
- mathematical form: `DM(x)=domain where x is validly interpreted`.
- programming contract: `DomainAssignment(domain_id, unit_id, domain, allowed_evidence_types, forbidden_transfers, confidence, residuals)`.
- linguistic function: separates literal, metaphorical, legal, scientific, grammatical uses.
- forbidden transitions: `domain_transfer_without_bridge`, `contradiction_without_domain`.
- residuals: `domain_without_designation`, `cross_domain_leakage`, `domain_unresolved`.
