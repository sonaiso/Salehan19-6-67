# Phase 7.4 — Arabic Mabni Logical-Pragmatic Control Layer

## Overview

The **Mabni** layer (طبقة المبني المنطقي-التداولي) implements deterministic analysis of Arabic indeclinable particles (الحروف والأدوات المبنية) that govern logical scope, pragmatic force, and certainty propagation in Arabic discourse.

Unlike content words (معرب), Mabni elements are morphologically fixed and carry systematic logical-pragmatic operators. This layer ensures the MCD system never confuses:
- **Emphasis** (توكيد) with **Evidence** (دليل)
- **Conditional** scope with **Assertion**
- **Restriction/Qasr** with **Evidence creation**

---

## Architecture

```
src/mcd/mabni/
├── mabni_schema.py              # Core enums: MabniType, LogicalFunction, PragmaticFunction, CertaintyEffect
├── mabni_operator.py            # MabniOperator dataclass (creates_evidence ALWAYS False)
├── pragmatic_vector.py          # MabniPragmaticVector (19 floats, evidence_creation <= 0.0)
├── mabni_registry.py            # Registry loading from data/mabni/mabni_registry_ar.json
├── ma_resolver.py               # ما disambiguation
├── man_resolver.py              # من disambiguation
├── in_resolver.py               # إن/إنّ/إنما disambiguation
├── la_resolver.py               # لا disambiguation
├── preposition_resolver.py      # Arabic preposition senses
├── conditional_engine.py        # إن/إذا/لو/لولا/لوما/كلما/... detection
├── counterfactual_engine.py     # لو/لولا/لوما counterfactual analysis
├── speech_act_resolver.py       # Speech act classification
├── attached_pronoun_unfolder.py # Attached pronoun analysis
├── demonstrative_resolver.py    # هذا/ذلك/هؤلاء/... resolution
├── relative_pronoun_resolver.py # الذي/التي/... resolution
├── answer_particle_resolver.py  # نعم/بلى/لا/كلا/... resolution
├── exception_restriction_engine.py  # إلا/غير/سوى/خلا/عدا/حاشا
├── qasr_engine.py               # إنما/لا...إلا/ما...إلا qasr analysis
├── emphasis_evidence_separator.py   # Separates emphasis from evidence
├── mabni_certainty_policy.py    # Per-operator certainty policy
├── mabni_graph_builder.py       # Operator relationship graph
├── mabni_trace_linker.py        # Unicode→Token→Operator→Graph→Evidence chain
├── mabni_unfolder.py            # Main orchestrator
├── mabni_report.py              # Markdown/JSON report generation
├── serializers.py               # JSON/JSONL serialization helpers
└── __init__.py                  # Public API
```

---

## Critical Invariants

### 1. Mabni operators NEVER create evidence

```python
# This will raise ValueError:
MabniOperator(..., creates_evidence=True)  # ❌

# This is always correct:
MabniOperator(..., creates_evidence=False)  # ✅
```

### 2. Emphasis ≠ Evidence

Arabic emphasis markers (إنّ, قد, oaths, لام التوكيد, نون التوكيد) increase **discourse force** only. They do NOT increase evidential weight or certainty scores.

```python
result = EmphasisEvidenceSeparator().analyze("إنّ زيداً قائم")
assert result.creates_evidence is False
assert result.certainty_increase == 0.0  # ALWAYS zero
```

### 3. Conditionals suspend judgment

Conditional structures (إن, إذا, لو, لولا, كلما, من, ما, مهما...) never assert that their protasis occurred. Judgment is ALWAYS suspended.

```python
result = ConditionalEngine().analyze("إن جاء زيد فأكرمه")
assert result.judgment_suspended is True  # ALWAYS
```

### 4. Counterfactuals enforce conditional_only policy

```python
result = CounterfactualEngine().analyze("لو درستَ لنجحتَ")
assert result.certainty_policy == "conditional_only"  # ALWAYS
```

### 5. Interrogatives are not assertions

```python
result = SpeechActResolver().classify("هل جاء زيد؟")
assert result.is_assertion is False
assert result.establishes_reality is False
```

### 6. بلى reverses negation (not نعم)

```python
result = AnswerParticleResolver().resolve("بلى", previous_question="ألم يجئ؟")
assert result.reverses_negation is True
```

### 7. Attached pronouns have unknown referent

```python
results = AttachedPronounUnfolder().unfold("رأيتُه")
assert results[0].referent_known is False  # ALWAYS
```

---

## CLI Commands

### `mabni-analyze`
Full Mabni analysis of Arabic text.

```bash
python -m mcd.cli mabni-analyze --text "ما جاء زيد" --output json
python -m mcd.cli mabni-analyze --text "إن جاء زيد فأكرمه" --output markdown
python -m mcd.cli mabni-analyze --text "بلى" --prev-question "ألم يجئ؟" --output summary
```

### `mabni-registry`
List or query the Mabni operator registry.

```bash
python -m mcd.cli mabni-registry --output table
python -m mcd.cli mabni-registry --surface "ما" --output json
```

### `mabni-certainty`
Evaluate certainty policy for operators in text.

```bash
python -m mcd.cli mabni-certainty --text "إن جاء زيد" --output summary
```

### `mabni-graph`
Build operator relationship graph.

```bash
python -m mcd.cli mabni-graph --text "ما جاء زيد" --output json
```

### `mabni-trace`
Trace the Mabni operator chain token by token.

```bash
python -m mcd.cli mabni-trace --text "ما جاء زيد" --output summary
```

---

## Mabni Types Covered

| Type | Particles | Notes |
|------|-----------|-------|
| negation | ما، لا، لم، لن، ليس | Various negation scopes |
| interrogative | هل، أ، من، ما، متى، أين | Question — not assertion |
| conditional | إن، إذا، لو، من، ما، مهما | Judgment always suspended |
| counterfactual | لو، لولا، لوما | Contrary-to-fact |
| emphasis | إنّ، قد، والله، لقد | Force only, not evidence |
| restriction | إنما، لا...إلا، ما...إلا | Scope restriction |
| exception | إلا، غير، سوى، خلا، عدا، حاشا | Scope modification |
| relative | الذي، التي، اللذان، الذين | Reference |
| demonstrative | هذا، هذه، ذلك، أولئك | Deixis |
| pronoun | ـه، ـها، ـهم، ـك، ـنا | referent_known=False always |
| preposition | ب، في، من، إلى، على، عن، ل، ك | Relation, not evidence |
| answer | نعم، بلى، لا، كلا | Context dependent |

---

## Data Files

All data is in `data/mabni/`. Key files:
- `mabni_registry_ar.json` — Master registry (38+ operators)
- `*_examples_ar.jsonl` — Usage examples per operator type
- `mabni_golden_examples_ar.jsonl` — Golden test cases
- `mabni_adversarial_examples_ar.jsonl` — Challenging/tricky cases

---

## Testing

```bash
# Run all mabni tests
PYTHONPATH=src python -m pytest tests/test_mabni_*.py tests/test_ma_resolver.py tests/test_man_resolver.py tests/test_in_resolver.py tests/test_la_resolver.py tests/test_conditional_engine.py tests/test_counterfactual_engine.py tests/test_speech_act_resolver.py tests/test_attached_pronoun_unfolder.py tests/test_answer_particle_resolver.py tests/test_exception_restriction_engine.py tests/test_qasr_engine.py tests/test_emphasis_evidence_separator.py tests/test_preposition_resolver.py -v
```
