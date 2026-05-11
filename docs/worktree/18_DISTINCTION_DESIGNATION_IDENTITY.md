# Distinction, Designation, Identity

## Designation (G)

- Epistemic definition: assignment of type/reference/function to a distinguished unit.
- Mathematical form: `G(u) = assign(u → type/reference/function/domain)`.
- Programming contract: `DesignationUnit(designation_id, distinguished_unit_id, assigned_type, assigned_identity, assigned_reference, assigned_function, assignment_basis, confidence, residuals)`.
- Linguistic function: binds lexical unit to role (e.g., proper noun, participle, operator).
- Forbidden transitions: `designation_without_distinction`, `wrong_assignment_basis`.
- Residuals: `ambiguous_assignment`, `unknown_type`, `unresolved_reference`.

## Identity (ID)

- Epistemic definition: continuity preservation of the same referent across context, scope, and time.
- Mathematical form: `ID(x1) = ID(x2)` when valid continuity path exists.
- Programming contract: `IdentityUnit(identity_id, mentions, reference_type, continuity_scope, identity_basis, confidence, residuals)`.
- Linguistic function: resolves anaphora/coreference and protects subject continuity.
- Forbidden transitions: `judgment_without_subject`, `homonym_confusion_as_identity`.
- Residuals: `identity_shift`, `temporal_identity_gap`, `unresolved_reference`.

## Governance constraints

- No designation without distinction.
- No judgment on a subject before identity continuity is either established or explicitly unresolved and downgraded.
