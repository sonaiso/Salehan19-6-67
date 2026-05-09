# Cognitive Reality-Based Learning — Phase 5.3

## Why Not Cat/Dog Classification?

Traditional ML classification maps inputs to discrete labels: `cat` or `dog`. This approach works for closed-world recognition tasks but fails for open-domain reasoning. The world is not a label space — it is a structured reality with entities, properties, actions, relations, causes, evidence, and certainty gradients.

The Reasoning Mind does not classify. It **frames**. Given an Arabic text, the system constructs a `RealityFrame` — a structured decomposition of what the text says, implies, and requires epistemically.

---

## Input → Label vs Reality → Frame

| Classical ML | Cognitive Curriculum |
|---|---|
| Input text → discrete label | Input text → RealityFrame |
| "cat" or "dog" | things, properties, actions, relations, causes, evidence |
| Single output | Structured multi-dimensional output |
| Closed world | Open world with uncertainty |
| No epistemic policy | Certainty policy required |

A `RealityFrame` captures:
- **What exists**: things
- **How things are**: properties
- **What happens**: actions
- **How things relate**: relations
- **Why things happen**: causes and effects
- **When and where**: times and places
- **With what**: instruments
- **How sure we are**: evidence and certainty policy

---

## The 8 Cognitive Layers

### Level 1: Things (أشياء)

Things are concrete or abstract entities that exist. A thing is not a property, not an action, not a relation. The model must learn to identify things without confusing them with their attributes or behaviors.

**Examples**: النار، الماء، API، قاعدة البيانات، الإنسان

**Key confusions to avoid**: `property_as_thing`, `action_as_thing`, `relation_as_thing`

### Level 2: Properties (خصائص)

Properties describe things. A property is an attribute that a thing possesses. Properties are not evidence, not certainty levels, not causes.

**Examples**: حار، قديم، رسمي، غير مدعوم، ضعيف

**Key confusions to avoid**: `property_as_evidence`, `property_as_certainty`

### Level 3: Actions (أفعال)

Actions describe what agents do to patients. An action requires an agent (who acts) and typically a patient (what is acted upon). Actions are not properties of things.

**Examples**: كتب، قرأ، صنّف، فحص، حلّل

**Key confusions to avoid**: `action_as_property`, `false_certainty`

### Level 4: Relations (علاقات)

Relations connect two entities through a semantic link. A relation is directional: source → relation → target. Relations are not things themselves.

**Examples**: يدعم، يعارض، يقوي، يوجب، لا يكفي

**Key confusions to avoid**: `relation_as_thing`, `similarity_as_evidence`

---

## Why Cause Differs from Effect

Cause and effect are asymmetric. Causes produce effects — reversing them produces false reasoning. The model must maintain causal direction:

- ✅ `غياب المصدر يسبب تعليق الحكم` (source absence causes judgment suspension)
- ❌ `تعليق الحكم يسبب غياب المصدر` (reversed — false)

**Key confusions to avoid**: `correlation_as_causation` — two events co-occurring does not mean one causes the other.

---

## Why Instrument is Not Evidence

An instrument (أداة) is a tool used to perform an action: API, Dataset, JSON, benchmark. Evidence (دليل) is information that supports or refutes a claim.

- `API` is an instrument for querying data — it is **not** evidence for a claim
- `staging environment` is a test place — it is **not** equivalent to `production`

**Key confusions to avoid**: `api_as_evidence`, `staging_equals_production`

---

## How Time Affects Certainty

A source may have been authoritative at time T₀ but stale by time T₁. The model must account for temporal qualification:

- `منذ سنة` (one year ago) → increases likelihood of staleness
- `مؤخرًا` (recently) → decreases staleness concern

Temporal context shifts the certainty policy: a stale source may require downgrading from `probable_knowledge` to `insufficient_evidence`.

---

## How Evidence Feeds Into Judgment Policy

Evidence types determine what kind of support is needed:

| Evidence Type | Description |
|---|---|
| `linguistic` | Lexical or grammatical support |
| `textual` | Quotation from a source text |
| `contextual` | Situational or background knowledge |
| `experimental` | Empirical test results |
| `historical` | Historical records |
| `rational` | Logical derivation |

When evidence is absent or insufficient, the certainty policy must reflect this:

| Condition | Policy |
|---|---|
| Full evidence | `certain_knowledge` or `near_certainty` |
| Partial evidence | `probable_knowledge` or `possible_knowledge` |
| Conflicting evidence | `insufficient_evidence` |
| No evidence | `suspend_judgment` |

---

## The 8-Level Curriculum Progression

```
Level 1: Things          → What exists?
Level 2: Properties      → How are things?
Level 3: Actions         → What happens?
Level 4: Relations       → How are things connected?
Level 5: Causes/Effects  → Why does something happen?
Level 6: Inst/Time/Place → Where, when, with what?
Level 7: Evidence/Cert.  → How sure can we be?
Level 8: Mixed Reasoning → Can we detect and resist adversarial patterns?
```

Each level builds on the previous. A system that cannot correctly identify things (Level 1) cannot reliably reason about evidence (Level 7).

---

## Connection to FPCL, MCD, NERL

### FPCL (Fractal Prompt Classification Layer)
The curriculum trains FPCL's judgment type classifier and evidence_need extractor. Levels 7–8 directly improve:
- `certainty_policy` assignment accuracy
- `evidence_needs` detection

### MCD (Minimal Cognitive Decoder)
The reality frame produced by curriculum training is the target output format for MCD. Levels 1–6 train the basic frame extraction capabilities.

### NERL (Nabhani Epistemic Reasoning Layer)
Levels 7–8 are directly aligned with NERL's epistemic discipline: suspend judgment without evidence, avoid false certainty, detect prompt injection risks.

---

## How Curriculum Raises Phase 5.2 Scores

Phase 5.2 established baseline scores across four dimensions. The curriculum targets each:

| Dimension | Baseline | Curriculum Target | How |
|---|---|---|---|
| Dataset Quality | 4.30 | ≥ 4.50 | 400 validated Arabic examples covering all 8 levels |
| Calibration | 4.30 | ≥ 4.50 | Levels 7–8 train certainty policy precision |
| Industrial Testing | 4.26 | ≥ 4.50 | IndustrialBridge exports L7/8 as test cases |
| Source Trust | 4.40 | ≥ 4.50 | Evidence need training reduces hallucination |

---

## Future Use

### Fine-Tuning
The 400-example curriculum dataset can be used as supervised fine-tuning (SFT) data for instruction-following models. Each `(input_text, expected_frame)` pair is a training example.

### RAG (Retrieval-Augmented Generation)
Level 7 evidence examples can be used to train the retrieval selector: what kind of document is needed for each query type?

### GraphRAG
The `RelationTriple` objects in each frame define a knowledge graph. GraphRAG can use these triples to construct entity-relationship graphs for Arabic reasoning.

### Curriculum-Driven Evaluation
The `CurriculumEvaluator` provides a structured rubric for evaluating any Arabic reasoning system against the 8-level cognitive hierarchy.
