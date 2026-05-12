# Rank Calculus (Governed Epistemic Escalation)

## Core Rule

\[
Rank(Evidence) \ge RequiredRank(Judgment)
\]

## Judgment Rank Constraints

- `RequiredRank(ZERO) = ZERO`
- `RequiredRank(HYPOTHESIS) = HYPOTHESIS`
- `RequiredRank(CERTIFICATE) = CERTIFICATE`

`FINAL_JUDGMENT` is transition-control metadata and not an additional public final status.

## Linking Minimum Evidence Rank

- `SYMBOLIC >= ZERO`
- `SEMANTIC >= HYPOTHESIS`
- `CONTEXTUAL >= WEAK_EVIDENCE`
- `CAUSAL >= STRONG_EVIDENCE`
- `INTERPRETIVE >= HYPOTHESIS`
- `EVIDENTIARY >= STRONG_EVIDENCE`
- `GOVERNED_CERTIFICATION >= CERTIFICATE`

## Escalation and Downgrade

Escalation is legal only when both link-type minimum rank and target-judgment rank are satisfied.

If residual uncertainty persists:

- proposed `CERTIFICATE` downgrades to `HYPOTHESIS`,
- proposed `HYPOTHESIS` downgrades to `ZERO`,
- `ZERO` remains `ZERO`.

## Uncertainty Propagation

Residuals propagate with the transition payload and must remain attached to:

- ProofObject,
- TraceGraph,
- ReverseTrace.

Residual presence blocks silent certainty inflation.

## Forbidden Rank Promotions

- No `ZERO -> CERTIFICATE` jump.
- No interpretation-to-certificate promotion.
- No semantic link direct final-judgment promotion.
- No final-judgment promotion without sufficient evidence rank.
