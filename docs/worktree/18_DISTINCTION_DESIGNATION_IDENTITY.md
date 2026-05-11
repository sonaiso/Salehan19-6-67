# 18 — Distinction, Designation, Identity

## Distinction
- epistemic definition: separates a processable unit from background.
- mathematical form: `D(x,b)=unit(x) where x is separated from background b`.
- programming contract: `DistinctionUnit(unit_id, source_signal, boundary, distinct_from, confidence, residuals)`.
- linguistic function: isolates tokens/phrases before assignment.
- forbidden transitions: `designation_without_distinction`, `silent_level_skip`.
- residuals: `unclear_boundary`, `overlapping_units`, `unsegmented_input`.

## Designation
- epistemic definition: assigns type/reference/function/domain to a distinguished unit.
- mathematical form: `G(u)=assign(u→type/reference/function/domain)`.
- programming contract: `DesignationUnit(designation_id, distinguished_unit_id, assigned_type, assigned_reference, assignment_basis, confidence, residuals)`.
- linguistic function: maps a token to grammatical/semantic role.
- forbidden transitions: `domain_without_designation`, `designation_without_distinction`.
- residuals: `ambiguous_assignment`, `unresolved_reference`, `unknown_type`.

## Identity
- epistemic definition: preserves sameness across context/time/reference.
- mathematical form: `ID(x1)=ID(x2)` when continuity path exists.
- programming contract: `IdentityUnit(identity_id, mentions, reference_type, continuity_scope, temporal_scope, identity_basis, confidence, residuals)`.
- linguistic function: resolves anaphora/coreference and continuity.
- forbidden transitions: `judgment_without_identity_resolution`, `silent_level_skip`.
- residuals: `identity_shift`, `homonym_confusion`, `temporal_identity_gap`.
