# Linking Taxonomy (Governed Epistemic Operation)

## Core Position

A link is a governed transition signal and is **not** automatically:

- interpretation,
- evidence,
- certificate,
- or final judgment.

For any link category:

\[
L_i : A \rightarrow B
\]

Legality is determined by governance, rank sufficiency, and forbidden transition checks.

## Linking Categories

- `SYMBOLIC`: structural symbol-level relation.
- `SEMANTIC`: meaning-level relation below evidence gate.
- `CONTEXTUAL`: domain-scope or situational relation.
- `CAUSAL`: directed causal relation claim.
- `INTERPRETIVE`: interpretation-level relation; non-certifying by default.
- `EVIDENTIARY`: evidence-bearing relation candidate.
- `GOVERNED_CERTIFICATION`: certification-eligible relation only when all gates pass.

## Domain Constraints

- `Interpretation != Certificate`.
- Semantic links remain below final judgment gates unless reclassified through governed evidence flow.
- Certification eligibility requires ProofObject, GovernanceGate, and ReverseTrace.
- Final public epistemic judgments remain constrained to: `ZERO`, `HYPOTHESIS`, `CERTIFICATE`.

## Residual Rules

Residuals are conserved through escalation and must remain visible in:

- ProofObject,
- TraceGraph,
- ReverseTrace.

Residuals are never erased during certainty movement.

## Forbidden Promotions

The following transitions are mechanically forbidden:

- `INTERPRETATION -> CERTIFICATE`
- `SEMANTIC_LINK -> FINAL_JUDGMENT`
- `ZERO -> CERTIFICATE`
- `HYPOTHESIS -> FINAL_JUDGMENT` without sufficient evidence rank
- `DEFINITION -> JUDGMENT`
- `INTERPRETATION -> EVIDENCE`
- `RELATION -> INFERENCE`
- `DALALA -> TANZIL` without a passed semantic governance gate

Additional constitutional forbidden transitions from the core remain active.

## Formal Transition Constraint

A link transition is legal only when:

\[
Legal(L_i) = Governance(L_i) \land Rank(L_i) \land Evidence(L_i) \land Trace(L_i)
\]

If any term is false, escalation is blocked or downgraded.
