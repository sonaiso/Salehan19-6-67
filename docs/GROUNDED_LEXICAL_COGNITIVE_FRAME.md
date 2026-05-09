# Grounded Lexical Cognitive Frame Layer (GLCFL)

## Overview

The GLCFL is the fourth major layer of the Minimal Cognitive Decoder (MCD) system. It grounds every word in a sentence to a real-world referent, builds relational frames, checks rule applicability, resolves conflicts, and classifies civilizational and value concepts.

---

## 1. Why an Ungrounded Word Carries No Knowledge

A word like "الحرية" (freedom) has a linguistic shape, but without grounding it carries no epistemic weight. Any reasoning built on an ungrounded word is floating — it has form but no substance. The GLCFL asks: *what does this word refer to in reality?*

---

## 2. What a Grounded Word Means

A **grounded word** (كلمة مُؤسَّسة) has:
- A **dāll** (دال) — the surface form
- A **madlūl** (مدلول) — the referent or meaning
- A **reality_ref** — a pointer to a real-world or knowledge-store entity
- A **certainty score** — how confident we are in the grounding

**Grounding statuses:**
| Status | Meaning |
|---|---|
| `GROUNDED` | Found in knowledge store with reality reference |
| `PARTIALLY_GROUNDED` | Linguistic meaning only, or ambiguous, or requires revelation evidence |
| `UNGROUNDED` | No referent found |
| `VERIFIED` | Confirmed through multiple independent sources |

---

## 3. How the Grounding Function Works (`LexicalGroundingEngine`)

1. Normalize the word (strip definite article ال)
2. Check if it's a **sharī term** (حرام, واجب, etc.) → always `PARTIALLY_GROUNDED` without revelation evidence
3. Check if it's **ambiguous** (علم, عين) → `PARTIALLY_GROUNDED` with `requires_context` note
4. Search the `ThingStore` by name → `GROUNDED` if found
5. Search `PropertyRegistry` → `GROUNDED` if found
6. Search `RelationStore` → `GROUNDED` if found
7. Linguistic meaning only → `PARTIALLY_GROUNDED`
8. Nothing found → `UNGROUNDED`

---

## 4. How a Sentence Becomes a RoleFrame

The `RoleFrameBuilder` uses rule-based Arabic heuristics:

**Arabic VSO order**: `فعل (verb) → فاعل (agent) → مفعول (patient)`

Rules:
- First word of sentence → detected as **verb** (action/event)
- First noun after verb → **agent** (فاعل)
- Second noun → **patient** (مفعول به)
- Word starting with `بـ` → **instrument** (آلة)
- `في` followed by noun → **place** (مكان)
- Time adverbs (أمس، اليوم، غدًا، صباحًا، مساءً) → **time** (زمان)

**Example:**
```
كتب زيد الدرس بالقلم في المدرسة أمس
→ action=كتب, agent=زيد, patient=الدرس, instrument=القلم, place=المدرسة, time=أمس
```

---

## 5. How Relations Become NisbahFrames

The `NisbahFrameBuilder` extracts **nisbah** (relational) frames from a `RoleFrame`:

| Component | NisbahType |
|---|---|
| agent | `AGENT_OF` |
| patient | `PATIENT_OF` |
| instrument | `INSTRUMENT_OF` |
| place | `PLACE_OF` |
| time | `TIME_OF` |
| cause | `CAUSES` |
| purpose | `AIMS_AT` |

Each `NisbahFrame` has: `source → [relation_type] → target`

---

## 6. How Manat Works

**Manat** (المناط) is the verification of whether a ruling's conditions are met in a given reality.

`ManatApplicabilityEngine.check(rule_id, rule_text, conditions, target_reality, target_properties)`:

| Score | Status |
|---|---|
| ≥ 0.8 | `APPLICABLE` |
| 0.4–0.8 | `PARTIALLY_APPLICABLE` |
| < 0.4 | `NOT_APPLICABLE` |
| No conditions | `SUSPENDED` |

---

## 7. How Tarjih Works

**Tarjih** (الترجيح) resolves conflicts between competing claims:

| Situation | Strategy |
|---|---|
| Claims address different non-conflicting aspects | `COMBINE` |
| One general, one specific | `SPECIFY` (prefer specific) |
| One absolute, one restricted | `RESTRICT` (prefer restricted) |
| One has much higher certainty | `PREFER` |
| No clear winner | `SUSPEND` |

Claims with `fake_evidence=True` are never preferred. Claims without a source have their certainty reduced.

---

## 8. How Human Differs from Individual

- **HumanFrame** represents the human species: rational, social, has needs and instincts
- **IndividualFrame** represents a specific person in a specific context

**Critical rule**: You cannot generalize from one individual's behavior to all of humanity. The `HumanIndividualModel.can_generalize_to_species()` always returns `False` with explanation.

---

## 9. How Society Is Modeled

A **society** (مجتمع) requires three elements:
1. **Shared ideas** (أفكار مشتركة)
2. **Collective feelings** (مشاعر جماعية)
3. **Systems/institutions** (أنظمة ومؤسسات)

A group of individuals without all three is NOT a society. The `SocietyModel` warns when any element is missing and keeps certainty low. A single individual's statement is never treated as public opinion.

---

## 10. How Civilization Differs from Civility

| Concept | Arabic | Definition | Example |
|---|---|---|---|
| **Civility** (مدنية) | أداة / شكل | A form, tool, or technique neutral in values | سيارة، هاتف، طب |
| **Civilization** (حضارة) | مفهوم / قيمة | A concept about life, values, and governance | الديمقراطية، الإسلام، الحرية |

**AI** (الذكاء الاصطناعي) is a special case: it is a **civility tool** but carries risk of civilizational value transfer (assumptions about humans, decision-making, knowledge, authority).

---

## 11. How Epistemic, Practical, and Sharī Values Differ

| Type | Arabic | Measure | Example Judgment |
|---|---|---|---|
| Epistemic | معرفي | صحيح / خطأ | الاستنتاج صحيح |
| Practical | عملي | نافع / ضار | الكذب ضار |
| Aesthetic | جمالي | جميل / قبيح | القصيدة جميلة |
| Sharī | شرعي | واجب / حرام / مندوب / مكروه / مباح | الكذب حرام |
| Social | اجتماعي | مقبول / مرفوض | السلوك مرفوض |

**Critical distinctions that must NEVER be confused:**
- `ضار` (harmful) ≠ `حرام` (haram)
- `نافع` (beneficial) ≠ `واجب` (wajib)
- `جميل` (beautiful) ≠ `جائز` (permissible)
- `مقبول اجتماعيًا` ≠ `صحيح معرفيًا`

Sharī judgments always require revelation evidence (نص وحي). Without it, certainty is lowered and a warning is added.

---

## 12. How GLCFL Connects to FPCL, MCD, NERL

```
User Input
    ↓
FPCL (Fractal Prompt Classification Layer)
    → classifies intent, domain, knowledge category
    ↓
MCD (Minimal Cognitive Decoder)
    → decodes claims, checks certainty, finds relations
    ↓
NERL (Nabhani Epistemic Reasoning Layer)
    → checks dal/madlul correspondence, rational judgment
    ↓
GLCFL (Grounded Lexical Cognitive Frame Layer)
    → grounds every word, builds role frames, extracts nisbah,
      checks manat, resolves tarjih, classifies values and civilization
    → outputs GroundedReasoningFrame with full epistemic audit trail
```

The `GroundedReasoningBuilder` orchestrates all four layers into a single cohesive pipeline.

---

## 13. CLI Examples

```bash
# Full grounding with JSON output
PYTHONPATH=src python -m mcd.cli ground "كتب زيد الدرس بالقلم في المدرسة أمس" --output json

# Value analysis
PYTHONPATH=src python -m mcd.cli ground "الكذب ضار أم حرام؟" --output json

# Civilization vs. civility
PYTHONPATH=src python -m mcd.cli ground "الذكاء الاصطناعي أداة مدنية أم مفهوم حضاري؟" --output json

# Society analysis
PYTHONPATH=src python -m mcd.cli ground "المجتمع يرفض الفساد" --output json

# Text report output
PYTHONPATH=src python -m mcd.cli ground "النار ساخنة" --output text

# With debug information
PYTHONPATH=src python -m mcd.cli ground "كتب زيد الكتاب" --debug --output json
```

### JSON Output Structure

```json
{
  "input_text": "...",
  "grounded_lexemes": [...],
  "role_frames": [...],
  "nisbah_frames": [...],
  "manat_results": [...],
  "usul_semantics": [...],
  "tarjih_results": [...],
  "social_frames": [...],
  "system_frames": [...],
  "civilization_frames": [...],
  "value_frames": [...],
  "final_status": "grounded|partially_grounded|ungrounded",
  "certainty_summary": 0.75,
  "warnings": [...]
}
```
