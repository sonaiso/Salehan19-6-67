# PAT-C — Preserved Ascent Transition Contract

## Scope

This specification defines the **formal governance contract** for PAT-C as a specification-layer ascent policy.
It does **not** change runtime behavior and does not introduce a new runtime judgment system.

## Sovereign Final Judgment Triad

PAT-C must map all governed outcomes to the existing repository triad only:

- `ZERO`
- `HYPOTHESIS`
- `CERTIFICATE`

Runtime equivalents remain unchanged:

- `zero`
- `hypothesis`
- `certificate`

No fourth final status is allowed.

## Architectural Chain Constraint

PAT-C is valid only when ascent remains aligned with the governing chain:

\[
\text{Reality} \rightarrow \text{Cognitive Distinction} \rightarrow \text{Linguistic Signification} \rightarrow \text{Conceptual Geometry} \rightarrow \text{Direct Meaning} \rightarrow \text{Licensed Implication} \rightarrow \text{Claim} \rightarrow \text{Evidence} \rightarrow \text{Judgment} \rightarrow \text{ReverseTrace}
\]

Any silent skip in this chain is forbidden.

## Mandatory Contract Fields per Architectural Unit

Each PAT-C governed unit must expose:

- `pre`
- `current`
- `post`
- `phi_in`
- `phi_out`
- `beta`
- `type`
- `order`
- `composition`
- `invariants`
- `forbidden`
- `residual`
- `judgment`

## Certificate Gate

A transition to `CERTIFICATE` is legal iff all are true:

- `ProofObject` exists
- `GovernanceGate` passed
- `ReverseTrace` complete
- evidence type matches claim type
- no blocking residual remains

Formal gate:

\[
\text{Certify}(x) = \text{ProofObject}(x) \land \text{GovernanceGate}(x) \land \text{ReverseTrace}(x) \land \text{EvidenceMatch}(x) \land \neg \text{BlockingResidual}(x)
\]

If any term is false, the final judgment must downgrade to `HYPOTHESIS` or `ZERO`.

## Forbidden Transitions

The following transitions are blocked by PAT-C governance:

- `root_or_pattern_as_factual_proof`
- `derivative_as_proof`
- `irab_as_factual_certainty`
- `emphasis_as_evidence`
- `metaphor_as_literal_certificate`
- `memory_as_external_evidence`
- `model_output_as_evidence`
- `tool_output_as_certificate_without_governance`
- `residual_erasure`
- `silent_level_skip`
- `certificate_without_proof_object`
- `certificate_without_governance_gate`
- `certificate_without_reverse_trace`

## Residual Conservation Law

Residuals are conserved and cannot be erased during ascent.
If a forbidden transition is detected, the corresponding residual must remain visible in output artifacts.

## PAT-C Output Mapping (Specification-Level Only)

PAT-C internal transition outcomes are interpreted at the specification layer and mapped to the sovereign triad:

- blocked/invalid ascent -> `ZERO`
- governed but incomplete ascent -> `HYPOTHESIS`
- fully gated ascent -> `CERTIFICATE`

This mapping is specification-only and does not redefine runtime semantics.
