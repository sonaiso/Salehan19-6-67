# Industrial Phase 3B-1 — Governed Quantity Mention Extraction

## Scope
Phase 3B-1 introduces the **first** governed quantitative-reasoning operator
in the project. It implements one local typed transition only:

```
PromptTextSpan / ArabicSpan -> QuantityMention
```

Phase 3B-1 deliberately does **not**:
- compute required speed,
- decide feasibility,
- emit `Judgment`, `Certificate`, `FinalAnswer`, or `ProjectConclusion`,
- solve the airport problem,
- promote any output above `JUDGMENT_HYPOTHESIS`.

It only discovers numeric/word quantity spans, binds each to a recognised
unit when possible, anchors the span back to `raw_prompt`, and emits typed
non-erasing residuals.

## Position in the Phase 3B chain
The full quantitative chain is built incrementally. Only step 1 is shipped
here. The remaining steps will be added as separate PRs:

| Step  | Transition                                      | Phase   |
| ----- | ----------------------------------------------- | ------- |
| 3B-1  | PromptTextSpan → QuantityMention                | this PR |
| 3B-2  | QuantityMention → DimensionedQuantity           | future  |
| 3B-3  | DimensionedQuantity → PhysicalRole              | future  |
| 3B-4  | PhysicalRoles → LawCandidate                    | future  |
| 3B-5  | LawCandidate + Roles → FeasibilityEvaluation    | future  |
| 3B-6  | FeasibilityEvaluation → QuantitativeProofObject | future  |

No `ZERO`, `HYPOTHESIS`, or `CERTIFICATE` quantitative judgment about the
airport problem may be issued before 3B-6 produces a governed
`QuantitativeProofObject` with full ReverseTrace and GovernanceGate.

## Operator contract
The extractor registers itself as a Phase 3A `OperatorContract`:

| Field                   | Value                                                 |
| ----------------------- | ----------------------------------------------------- |
| `operator_id`           | `quantity.extract.arabic_mention`                     |
| `layer_from`            | `PromptTextSpan`                                      |
| `layer_to`              | `QuantityMention`                                     |
| `input_type`            | `ArabicSpan`                                          |
| `output_type`           | `QuantityMention`                                     |
| `missing_gate`          | `quantity_extraction_gate`                            |
| `gates`                 | `numeric_or_number_word_present`, `unit_expression_present` |
| `evidence_requirements` | `span_trace_required`                                 |
| `rank`                  | `JUDGMENT_HYPOTHESIS` (any higher rank is rejected)   |
| `reverse_trace_required`| `True`                                                |
| `forbidden_outputs`     | `feasibility_judgment`, `Judgment`, `Certificate`, `FinalAnswer`, `ProjectConclusion` |

The contract is composable as the **first step** of the Phase 3B chain
under Phase 3A+ composition governance (`PromptTextSpan → QuantityMention →
DimensionedQuantity → …`). It is rejected if placed anywhere except first
because adjacent layer/type checks fail.

## QuantityMention shape
Every extracted mention is a frozen `QuantityMention` dataclass containing:

- `raw_text` — verbatim slice of the original prompt
- `value` / `normalized_value` — integer or float numeric value when known
- `unit_raw` / `unit_normalized` — original unit token(s) and canonical form
- `span_start` / `span_end` — anchors into `raw_prompt`
- `rank` — always `JUDGMENT_HYPOTHESIS`
- `confidence` — 0.7 when both number and unit resolve, otherwise 0.3
- `residuals` — non-erasing typed residuals
- `trace_anchor` — `{label, start, end, text}` snapshot for ReverseTrace

## Recognised lexicon
- **Digits:** Arabic-Indic (`٠–٩`), Eastern-Arabic-Indic (`۰–۹`), and Western
  (`0–9`); optional decimal `.` or `,` separators.
- **Number words (small):** `صفر`, `واحد(ة)`, `اثنان/اثنين/اثنتان/اثنتين`,
  `ثلاثة/ثلاث`, `أربعة/اربعة/أربع/اربع`, `خمسة/خمس`, `ستة/ست`, `سبعة/سبع`,
  `ثمانية/ثماني`, `تسعة/تسع`, `عشرة/عشر`.
- **Single-token units:** `كم`, `كيلو` (ambiguous → residual), `كيلومتر`,
  `كلم`, `متر`, `أمتار`, `دقيقة`, `دقائق`, `د`, `ثانية`, `ثواني`, `ث`,
  `ساعة`, `ساعات`, `س`, `يوم`, `أيام`, `ميل`, `أميال`.
- **Compound speed units:** `كم/ساعة`, `كم بالساعة`, `كم في الساعة`,
  `كيلومتر/ساعة`, `كيلومتر بالساعة`, `متر/ثانية`, `متر بالثانية`, etc.

## Residual taxonomy
All quantitative residuals are registered as blocker-level entries in
`mcd.core.residual_taxonomy` under the `fractal_operator` family:

| Code                                  | Trigger                                                    |
| ------------------------------------- | ---------------------------------------------------------- |
| `quantity_number_without_unit`        | A number is found with no recognised following unit.       |
| `quantity_unit_without_number`        | A unit token is found with no preceding number.            |
| `quantity_unit_ambiguous`             | A unit alias is recognised but inherently ambiguous (e.g. `كيلو` → km/kg). |
| `quantity_word_number_unresolved`     | Reserved for future Arabic compound number-word parsing.   |
| `quantity_span_trace_missing`         | A mention lacks a valid `trace_anchor` span.               |
| `quantity_extraction_payload_invalid` | The serialized payload structure is invalid or over-ranked.|

All codes are `BLOCKER` severity and `blocks_certificate=True`, so any
attempt to certificate a downstream consumer while these residuals remain
will be blocked by `has_blocking_residuals`.

## Governance guarantees
- The extractor is a single-transition local operator — multi-transition
  shortcuts (e.g. `PromptTextSpan -> Judgment`) are rejected by
  `OperatorContract.validate`.
- The extractor refuses certificate rank: even if a caller passes
  `rank=JUDGMENT_CERTIFICATE` to `build_quantity_extraction_operator_contract`,
  it is silently clamped to `JUDGMENT_HYPOTHESIS`.
- Payload deserialization downgrades any incoming `CERTIFICATE` rank to
  `HYPOTHESIS`, preventing silent certificate smuggling through round-trip.
- Every mention is anchored to `raw_prompt`; the validator emits
  `quantity_span_trace_missing` if the anchor is dropped.
- Residuals are non-erasing: they are aggregated on every payload build and
  preserved through serialize → deserialize.

## What is still missing
Phase 3B-1 cannot answer the airport problem. The chain still needs:
1. Unit normalization (`km`, `minute` → SI `m`, `s`).
2. Role binding (which quantity is distance, time, or speed limit).
3. Law selection (`v = d / t`).
4. Constraint evaluation against the speed limit.
5. A `QuantitativeProofObject` carrying ReverseTrace and GovernanceGate.

Until those phases land, the project must continue to return
`HYPOTHESIS` for quantitative motion-constraint prompts — but with a
populated `quantity_mentions` payload that shows *exactly which numbers
and units were understood* and *which transitions are still broken*.
