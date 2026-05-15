# PRIOR_AWARE_BASELINE_ABLATION_REPORT (#108)

## Scope
- This report defines prior-aware ablation measurement for benchmark dataset #105.
- It does not perform training.
- It does not collect external GPT/Kimi outputs.
- It does not claim trained FGN.
- It does not claim artificial consciousness.
- It does not claim global CERTIFICATE.
- Global theorem status remains `STRONG_HYPOTHESIS`.

## Prior-aware metrics
1. `prior_rule_coverage_rate`  
   Fraction of benchmark cases matched by at least one Golden Prior rule.

2. `prior_blocker_activation_rate`  
   Fraction of cases where prior certificate blockers activate.

3. `prior_missing_evidence_rate`  
   Fraction of prior-matched cases missing prior-required evidence items.

4. `prior_residual_preservation_rate`  
   Fraction of prior-matched cases where expected residuals are preserved and not silently dropped.

5. `prior_false_certificate_delta`  
   Delta between with-prior and without-prior `false_certificate_rate`.

6. `prior_overblocking_delta`  
   Delta between with-prior and without-prior `overblocking_rate`.

7. `prior_gettier_detection_delta`  
   Delta between with-prior and without-prior `gettier_detection_rate`.

8. `prior_trace_enforcement_delta`  
   Delta between with-prior and without-prior `reverse_trace_coverage`.

9. `prior_coverage_gap_residual`  
   Explicit residual emitted when no prior rule matches a case (`prior_coverage_gap`), including gap count and case IDs.

## Why GPKB is not optional
- Governance requires pre-scoped knowledge of what is provable, what evidence is mandatory, and what transitions are forbidden.
- Without GPKB, benchmark outcomes can look numerically acceptable while still violating blocked transitions that are known a priori.
- Reliable governance needs explicit prior constraints before decision ascent, not post-hoc correction.

## Why priors should block unjustified certificates
- Prior blockers encode known invalid transitions such as score-only or CI-pass-only ascent.
- Prior evidence requirements prevent certificate ascent when required supporting evidence is absent.
- Prior residual expectations preserve unresolved uncertainty and prevent residual erasure during escalation.

## Why priors must not overblock valid STRONG decisions
- Prior checks target certificate/candidate ascent conditions, not all STRONG decisions.
- STRONG remains valid when governance constraints are satisfied for strong-level support while certificate gates remain blocked.
- Overblocking is measured explicitly via `prior_overblocking_delta` to guard against excessive conservative collapse.

## Missing prior coverage handling
- If a case has no matching prior rule, the system emits `prior_coverage_gap`.
- Default policy blocks `CERTIFICATE` under missing prior coverage.
- Case-level decision stays at `HYPOTHESIS` or lower unless explicit non-prior certificate policy permits ascent.
- Missing coverage is treated as residual, never silently ignored.
