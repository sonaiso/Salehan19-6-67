# Universal, Particular, Domain

## Universal (UP-U)

- Epistemic definition: concept predicable over many particulars.
- Mathematical form: `Universal(U) ⇔ ∃x,y,z : predicable(U, x,y,z)`.
- Programming contract: `UniversalConcept(concept_id, label, applies_to_many, necessary_features, domain, scope, residuals)`.
- Linguistic function: abstracts recurring meaning classes.
- Forbidden transitions: `universal_to_particular_without_applicability`.
- Residuals: `overgeneralization`, `scope_ambiguity`.

## Particular (UP-P)

- Epistemic definition: determined referent not predicable over many in the same sense.
- Mathematical form: `Particular(p) ⇔ ¬applies_to_many(p)`.
- Programming contract: `ParticularUnit(particular_id, reference, designation_id, time_scope, place_scope, identity_unit_id, residuals)`.
- Linguistic function: anchors claims to indexed referents.
- Forbidden transitions: `subject_without_designation`, `subject_without_identity_context`.
- Residuals: `missing_context`, `indexing_gap`.

## Domain (DM)

- Epistemic definition: validity scope for interpretation, evidence, and judgment transfer.
- Mathematical form: `DM(x) = domain in which x is validly interpreted`.
- Programming contract: `DomainAssignment(domain_id, unit_id, domain, assignment_basis, allowed_evidence_types, forbidden_transfers, confidence, residuals)`.
- Linguistic function: disambiguates same expressions across legal, linguistic, scientific, or metaphorical usage.
- Forbidden transitions: `domain_without_designation`, `domain_transfer_without_bridge`, `no_contradiction_without_domain`.
- Residuals: `cross_domain_leak`, `domain_ambiguity`, `invalid_transfer_attempt`.

## Applicability contract

Universal-to-particular projection must be blocked unless applicability conditions are checked and satisfied.
