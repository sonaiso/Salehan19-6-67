# Epistemic Traceability Quality Lock — Phase 7.1.3

## Overview

Phase 7.1.3 adds an **epistemic quality layer** on top of the structural
traceability introduced in Phase 7.1.2.  Structural traceability proves that
every Unicode code point is tracked through the trace chain.  Epistemic
traceability proves that the **reason** behind each judgment is sound.

---

## 1. Why Structural Traceability Is Not Enough

A system that correctly traces Unicode → Tokens → Nodes → Judgment is
structurally correct, but it can still assign `strong_knowledge` to:

- An **ambiguous** word like "عين" (which can mean eye, spring, spy, or
  source depending on context).
- A **metaphor** like "المجتمع مريض" (society is sick) — which is not a
  literal medical diagnosis.
- An **unsupported generalization** like "جميع الناس يحبون الحرية" with no
  source.
- A claim that API output or model output constitutes **evidence**.

Structural traceability would give all of these `strong_knowledge` because
no evidence-missing signal word (بلا مصدر, etc.) is present.  Epistemic
traceability adds a second layer of rules that checks the **meaning** of the
judgment, not just its chain.

---

## 2. Difference: TraceValidator vs EpistemicTraceValidator

| Concern | TraceValidator (Phase 7.1.2) | EpistemicTraceValidator (Phase 7.1.3) |
|---------|------------------------------|---------------------------------------|
| Unicode coverage | ✅ Every code point has a trace_id | Not checked |
| No orphan tokens | ✅ Every token in evidence chain | Not checked |
| `strong_knowledge` validity | ❌ Not checked | ✅ Requires evidence_status = present |
| Ambiguous terms | ❌ Not detected | ✅ Detected, forces context_required |
| Metaphor | ❌ Not detected | ✅ Detected, forces hypothesis |
| Universal quantifiers | ❌ Not checked | ✅ Requires source unless definitional |
| API/model-as-evidence | ❌ Not checked | ✅ Blocked, forces unverified |
| Prompt injection | ✅ Detected (fake) | ✅ Detected (contaminated + reject) |
| Score target | traceability_score ≥ 0.99 | epistemic_trace_score ≥ 0.95 |

---

## 3. How Unicode Affects the Judgment

The full chain is:

```
Unicode code point
  └─► UnicodeTraceUnit (trace_id)
        └─► GraphemeTrace (grapheme cluster)
              └─► TokenTrace (normalized word)
                    ├─► EvidenceTrace  ← is this token a signal?
                    ├─► CertaintyTrace ← does this token raise/lower certainty?
                    ├─► NodeTraceLink  ← does this token map to a concept node?
                    ├─► EdgeTraceLink  ← does this token support a relation?
                    └─► JudgmentTrace  ← final decision (answer/suspend/reject)
```

For example, the Arabic character `ع` in "عين" contributes to:
- A `UnicodeTraceUnit` with its Unicode code point.
- A `GraphemeTrace` as part of the grapheme cluster "عين".
- A `TokenTrace` with surface="عين", normalized="عين".
- An `EvidenceTrace` with status="context_required" (ambiguous term).
- A `CertaintyTrace` with policy="suspend".
- A `JudgmentTrace` with final_decision="suspend", warnings=["ambiguous_term"].

---

## 4. Missing Evidence Tracing

The system detects the following signals that force `evidence_status = "missing"`:

| Signal | Example |
|--------|---------|
| "بلا" (without) before مصدر/دليل | "هذا صحيح بلا مصدر" |
| "بدون" (without) before مصدر/دليل | "لا يوجد دليل" |

These signals are detected at the **token bigram level** (not substring) to
avoid false positives like "المصدر: صحيح البخاري" (providing a source).

---

## 5. Ambiguity Tracing

The following Arabic terms are flagged as inherently ambiguous when they appear
as the primary semantic token without disambiguating context:

`عين`, `علم`, `حق`, `عدل`, `نظام`

Detection rule:
- If ≥50% of semantic tokens are ambiguous terms AND total semantic tokens ≤ 3
  → `evidence_status = "context_required"`, `certainty_policy = "suspend"`,
  `final_decision = "request_evidence"`

"عين" alone → context_required.  
"في عين زيد" → not forced (multiple semantic tokens, low ambiguity ratio).

---

## 6. Metaphor Tracing

Known metaphor patterns (subject/predicate pairs):

| Pattern | Example |
|---------|---------|
| (المجتمع / مريض) | "المجتمع مريض" |
| (العلم / نور) | "العلم نور والجهل ظلام" |
| (الجهل / ظلام) | "الجهل ظلام" |

When a metaphor is detected:
- `certainty_policy = "hypothesis"` (not literal fact)
- `final_decision = "suspend"` (hypothesis doesn't yield answer)
- `warnings = ["metaphor_detected", "not_literal"]`

---

## 7. False Certainty Tracing

The following patterns produce false certainty and are blocked:

| Pattern | Status Forced | Certainty |
|---------|---------------|-----------|
| API/model token (api, gpt, النموذج) | unverified | suspend |
| Universal quantifier without source | source_required | suspend |
| Ambiguous term (عين, علم, ...) | context_required | suspend |
| Prompt injection | contaminated | suspend → reject |

**Universal quantifier exemptions:** If the claim also contains a definitional
or religious/logical context word (يموت, سيموت, الله, الصلاة, واجب, etc.),
the universal quantifier does NOT force source_required.

Examples:
- "كل من في الدنيا سيموت" → definitional (يموت/سيموت) → strong_knowledge ✅
- "الصلاة واجبة على كل مسلم" → religious (الصلاة, واجب) → strong_knowledge ✅
- "جميع الناس يحبون الحرية" → no definitional context → source_required ✅

---

## 8. From Symbol to Explainable Decision

Every judgment is now fully explainable from the Unicode level:

```
Unicode "ج" + "م" + "ي" + "ع"
  → Token "جميع" (universal quantifier)
    → Evidence: source_required (universal without definitional context)
      → Certainty: suspend (evidence status is source_required)
        → Judgment: final_decision=suspend
          → Explanation: "Decision 'suspend' based on evidence_status='source_required',
             certainty_policy='suspend'. Universal quantifier without definitional/source
             context. Source required."
```

---

## New Modules

| Module | Purpose |
|--------|---------|
| `epistemic_trace_validator.py` | Validates epistemic correctness of bundles |
| `contribution_matrix.py` | Maps each token to its contribution types |
| `trace_graph_consistency.py` | Checks internal consistency of trace graph |

## New CLI Commands

```bash
# Validate a single text epistemically
python -m mcd.cli trace-epistemic-validate --text "عين" --output markdown

# Validate all 50 golden examples
python -m mcd.cli trace-epistemic-report --output markdown

# Show contribution matrix for a text
python -m mcd.cli trace-contribution --text "النموذج قال إن كل الشركات تستخدم GraphRAG بلا مصدر" --output json

# Check trace-graph consistency
python -m mcd.cli trace-graph-consistency --text "كتب زيد الدرس بالقلم في المدرسة أمس" --output json
```

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Golden examples corrected epistemically | ✅ 8 examples corrected |
| EpistemicTraceValidator exists | ✅ |
| epistemic_trace_score ≥ 0.95 | ✅ 1.0000 |
| TraceContributionMatrix exists | ✅ |
| TraceGraphConsistency exists | ✅ |
| "عين" → no strong_knowledge without context | ✅ context_required |
| "المجتمع مريض" → hypothesis, not literal | ✅ |
| "جميع الناس..." → requires source | ✅ source_required |
| "بلا مصدر" → forces suspend | ✅ |
| prompt injection → reject/suspend | ✅ reject + contaminated |
| API/GPT/model output is not evidence | ✅ unverified |
| All tests pass (1803 total) | ✅ |
| No API changes | ✅ |
| No GraphRAG | ✅ |
| No GPT calls | ✅ |
| No network calls | ✅ |
