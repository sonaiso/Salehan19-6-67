# Curriculum Dataset Specification — Phase 5.3

This document defines the JSONL schema for each of the 8 curriculum levels.

---

## Common Schema

Every JSONL line is a JSON object conforming to the `CognitiveUnit` schema:

```json
{
  "unit_id": "L01-0001",
  "input_text": "string — Arabic text input",
  "level": 1,
  "target_layer": "thing",
  "expected_frame": { ... },
  "expected_warnings": ["warning_id", ...],
  "forbidden_confusions": ["confusion_id", ...],
  "evidence_need": ["linguistic", ...],
  "certainty_policy": "certain_knowledge",
  "difficulty": "easy",
  "tags": ["things"],
  "metadata": {}
}
```

### `expected_frame` Schema

```json
{
  "things": ["string", ...],
  "properties": ["string", ...],
  "actions": ["string", ...],
  "agents": ["string", ...],
  "patients": ["string", ...],
  "instruments": ["string", ...],
  "times": ["string", ...],
  "places": ["string", ...],
  "causes": ["string", ...],
  "effects": ["string", ...],
  "relations": [
    {"source": "string", "relation": "string", "target": "string", "qualifier": null}
  ],
  "evidence_need": ["string", ...],
  "certainty_policy": "string",
  "warnings": ["string", ...]
}
```

### Valid Values

| Field | Valid Values |
|---|---|
| `level` | 1, 2, 3, 4, 5, 6, 7, 8 |
| `target_layer` | thing, property, action, relation, cause, effect, instrument, time, place, evidence, certainty, mixed_reasoning |
| `certainty_policy` | certain_knowledge, probable_knowledge, possible_knowledge, insufficient_evidence, near_certainty, suspend_judgment |
| `difficulty` | easy, medium, hard, adversarial |

---

## Level 1: Things

**File**: `level_01_things_ar.jsonl`  
**Target Layer**: `thing`  
**Certainty Policy**: `certain_knowledge`

A Level 1 unit identifies a single entity as a thing. The `expected_frame.things` field must be non-empty.

**Example**:
```json
{
  "unit_id": "L01-0001",
  "input_text": "النار شيء.",
  "level": 1,
  "target_layer": "thing",
  "expected_frame": {
    "things": ["النار"],
    "certainty_policy": "certain_knowledge"
  },
  "forbidden_confusions": ["property_as_thing", "action_as_thing"],
  "certainty_policy": "certain_knowledge",
  "difficulty": "easy",
  "tags": ["things"]
}
```

---

## Level 2: Properties

**File**: `level_02_properties_ar.jsonl`  
**Target Layer**: `property`  
**Certainty Policy**: `probable_knowledge`

A Level 2 unit identifies a property of an entity. Both `expected_frame.things` and `expected_frame.properties` must be non-empty.

**Example**:
```json
{
  "unit_id": "L02-0001",
  "input_text": "النار حارة.",
  "level": 2,
  "target_layer": "property",
  "expected_frame": {
    "things": ["النار"],
    "properties": ["حارة"],
    "certainty_policy": "probable_knowledge"
  },
  "forbidden_confusions": ["property_as_evidence", "property_as_certainty"],
  "certainty_policy": "probable_knowledge"
}
```

---

## Level 3: Actions

**File**: `level_03_actions_ar.jsonl`  
**Target Layer**: `action`  
**Certainty Policy**: `probable_knowledge`

A Level 3 unit identifies an agent–action–patient triple. The frame must include `actions`, `agents`, `patients`, and at least one `relations` entry.

**Example**:
```json
{
  "unit_id": "L03-0001",
  "input_text": "زيد كتب التقرير.",
  "level": 3,
  "target_layer": "action",
  "expected_frame": {
    "things": ["زيد", "التقرير"],
    "actions": ["كتب"],
    "agents": ["زيد"],
    "patients": ["التقرير"],
    "relations": [
      {"source": "زيد", "relation": "agent_of", "target": "كتب", "qualifier": null},
      {"source": "التقرير", "relation": "patient_of", "target": "كتب", "qualifier": null}
    ],
    "certainty_policy": "probable_knowledge"
  }
}
```

---

## Level 4: Relations

**File**: `level_04_relations_ar.jsonl`  
**Target Layer**: `relation`  
**Certainty Policy**: `probable_knowledge`

A Level 4 unit identifies a semantic relation between two entities. The frame must include `relations` with at least one entry.

**Valid relation types**: supports, contradicts, strengthens, requires, insufficient_for, not_equal_to, carries, cannot_be, constrains, determines

**Example**:
```json
{
  "unit_id": "L04-0001",
  "input_text": "الدليل يدعم الحكم.",
  "level": 4,
  "target_layer": "relation",
  "expected_frame": {
    "things": ["الدليل", "الحكم"],
    "relations": [
      {"source": "الدليل", "relation": "supports", "target": "الحكم", "qualifier": null}
    ],
    "certainty_policy": "probable_knowledge"
  }
}
```

---

## Level 5: Causes and Effects

**File**: `level_05_causes_effects_ar.jsonl`  
**Target Layer**: `cause`  
**Certainty Policy**: `probable_knowledge`

A Level 5 unit identifies a causal relationship. The frame must include both `causes` and `effects`.

**Example**:
```json
{
  "unit_id": "L05-0001",
  "input_text": "غياب المصدر يسبب تعليق الحكم.",
  "level": 5,
  "target_layer": "cause",
  "expected_frame": {
    "causes": ["غياب المصدر"],
    "effects": ["تعليق الحكم"],
    "relations": [
      {"source": "غياب المصدر", "relation": "causes", "target": "تعليق الحكم", "qualifier": null}
    ],
    "certainty_policy": "probable_knowledge"
  },
  "forbidden_confusions": ["correlation_as_causation", "false_certainty"]
}
```

---

## Level 6: Instruments, Times, and Places

**File**: `level_06_instruments_times_places_ar.jsonl`  
**Target Layer**: `instrument`  
**Certainty Policy**: `probable_knowledge`

A Level 6 unit grounds an action in context: who used what tool, where, and when.

**Example**:
```json
{
  "unit_id": "L06-0001",
  "input_text": "استخدم زيد API لـفحص المنصة أمس.",
  "level": 6,
  "target_layer": "instrument",
  "expected_frame": {
    "things": ["زيد", "API"],
    "actions": ["فحص"],
    "agents": ["زيد"],
    "instruments": ["API"],
    "times": ["أمس"],
    "places": ["المنصة"],
    "certainty_policy": "probable_knowledge"
  },
  "forbidden_confusions": ["api_as_evidence", "staging_equals_production"]
}
```

---

## Level 7: Evidence and Certainty

**File**: `level_07_evidence_certainty_ar.jsonl`  
**Target Layer**: `evidence`  
**Certainty Policy**: `insufficient_evidence` or `suspend_judgment`

Level 7 units train epistemic discipline. The frame must include `evidence_need`. Certainty policy must be `insufficient_evidence` or `suspend_judgment`.

**Valid evidence types**: linguistic, textual, contextual, experimental, historical, rational

**Valid warnings**: source_required, stale_source, conflict_detected, injection_risk, insufficient_evidence

**Example**:
```json
{
  "unit_id": "L07-0001",
  "input_text": "الجواب يحتاج دليلًا من نوع linguistic ليكون مقبولًا.",
  "level": 7,
  "target_layer": "evidence",
  "expected_frame": {
    "evidence_need": ["linguistic"],
    "certainty_policy": "insufficient_evidence",
    "warnings": ["source_required", "stale_source"]
  },
  "expected_warnings": ["source_required", "stale_source"],
  "evidence_need": ["linguistic"],
  "certainty_policy": "insufficient_evidence",
  "forbidden_confusions": ["near_certainty_without_source", "evidence_from_popularity"]
}
```

---

## Level 8: Mixed Reasoning (Adversarial)

**File**: `level_08_mixed_reasoning_ar.jsonl`  
**Target Layer**: `mixed_reasoning`  
**Certainty Policy**: `suspend_judgment`  
**Difficulty**: `adversarial`

Level 8 units are adversarial scenarios where a system might be tricked into false certainty, fabricated statistics, or other epistemic failures.

**Rules**:
- `difficulty` must be `adversarial` or `hard`
- `forbidden_confusions` must be non-empty
- `evidence_need` must include `textual` and `contextual`
- `certainty_policy` must be `suspend_judgment`

**Valid adversarial warnings**: fabricated_statistic, false_certainty, harm_equals_haram, follow_injection, ignore_conflict, present_stale_as_current, accept_ambiguous_without_context

**Example**:
```json
{
  "unit_id": "L08-0001",
  "input_text": "زيد قال إن الجواب يقيني بلا مصدر.",
  "level": 8,
  "target_layer": "mixed_reasoning",
  "expected_frame": {
    "things": ["زيد"],
    "agents": ["زيد"],
    "evidence_need": ["textual", "contextual"],
    "certainty_policy": "suspend_judgment",
    "warnings": ["fabricated_statistic", "false_certainty", "ignore_conflict"]
  },
  "expected_warnings": ["fabricated_statistic", "false_certainty", "ignore_conflict"],
  "forbidden_confusions": ["fabricated_statistic", "false_certainty", "ignore_conflict"],
  "evidence_need": ["textual", "contextual"],
  "certainty_policy": "suspend_judgment",
  "difficulty": "adversarial",
  "tags": ["mixed_reasoning", "adversarial"]
}
```
