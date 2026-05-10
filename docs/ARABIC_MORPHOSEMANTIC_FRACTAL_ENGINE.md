# Arabic Morphosemantic Fractal Engine — Phase 7.3

## Overview

The **Arabic Morphosemantic Fractal Engine** implements a *folded cognitive graph* representation of Arabic morphological analysis. Every Arabic word is treated as a compressed encoding of semantic, ontological, and relational information across multiple axes. The engine unfolds this encoding into a navigable graph structure called a **FoldedWordGraph**.

This phase is built entirely from first principles in pure Python — no external APIs, no network calls, no model inference.

---

## Architecture

```
Word (surface form)
  │
  ▼
MorphophonologicalNormalizer    ── strips diacritics, normalises hamza/alif
  │
  ▼
MorphosemanticTraceLinker       ── entry point; orchestrates all subsystems
  │
  ├─► RootOntology              ── triconsonantal root lookup
  ├─► PatternOperatorRegistry   ── 16+ pattern operators with semantic vectors
  ├─► MasdarEventOntology       ── masdar (verbal noun) event classes
  ├─► ContextualPatternResolver ── ambiguity resolution for polysemous words
  │
  ▼
FoldedWordGraph                 ── dataclass: nodes + edges + semantic vectors
  │
  ├─► FoldedWordUnfolder        ── expands graph to readable Markdown table
  ├─► ConceptCenterMapper       ── maps graph → 17-axis ConceptCenter
  └─► PatternCertaintyScorer    ── assigns certainty scores per pattern
```

### Supporting engines

| Module | Purpose |
|--------|---------|
| `nisba_engine.py` | Derives relational adjectives (نِسبة) |
| `industrial_masdar_engine.py` | Industry/craft masdar derivation |
| `diminutive_operator.py` | Diminutive (تصغير) forms |
| `broken_plural_transformer.py` | Broken plural (جمع التكسير) lookup |
| `agency_patienthood_matrix.py` | Thematic role matrix |
| `causation_transformation_engine.py` | Causation chain analysis |
| `place_time_instrument_resolver.py` | ظرف/آلة noun resolution |
| `qiyasi_samai_shadh_registry.py` | Analogical/heard/exceptional classification |
| `root_family_graph.py` | Full root family clustering |
| `morphosemantic_pattern_miner.py` | Pattern frequency mining |
| `serializers.py` | JSON and Markdown output |
| `jamid_essence_ontology.py` | Non-derived (jamid) essence terms |
| `essence_attribute_binding.py` | Maps essences to their attributes |

---

## Key Concepts

### 1. Root Ontology (الجذر)

Every Arabic word traces back to a **triconsonantal root** (جذر ثلاثي). The engine stores roots as `RootNode` dataclasses with:

- **radicals** — the 3 consonants
- **semantic\_core** — the core meaning in Arabic
- **event\_potential** — which event types this root can express
- **causation\_potential** / **metaphor\_potential** — float scores (0–1)
- **transitivity\_potential** — `transitive | intransitive | both`

```python
from mcd.morphosemantics.root_ontology import get_root_by_id
root = get_root_by_id("ktb")
# root.radicals == ["ك", "ت", "ب"]
# root.semantic_core == "الكتابة والتدوين"
```

### 2. Pattern Operator (الوزن الصرفي)

A **PatternOperator** is a morphological pattern (وزن) annotated with a 12-dimensional **operator vector** that captures its semantic contribution:

| Dimension | Meaning |
|-----------|---------|
| `agency` | How strongly this pattern marks the doer (فاعِل) |
| `patienthood` | How strongly it marks the receiver (مَفعول) |
| `causation` | Causative potential |
| `place` | Place/location marking (اسم المكان) |
| `time` | Time marking (اسم الزمان) |
| `instrument` | Instrument marking (اسم الآلة) |
| `nisba` | Relational adjective marking |
| `comparison` | Comparative/intensification |
| `multiplication` | Plurality/abundance |
| `transformation` | Semantic transformation (derived stems) |
| `masdar` | Verbal noun marking |
| `jamid` | Non-derived essence |

Built-in patterns include: `faail`, `mafuul`, `mafal_place`, `mafala_place`, `faaaal_intense`, `istafala_verb`, `tafaala_reflex`, `faiil_attr`, `fuayyil_dim`, `afaal_plural`, `fiaal_plural`, `fuuul_plural`, `fual_plural`, `nisba_yaa`, `mustafl_patient`, `mufaail_agent`, `fiaala_masdar_craft`.

### 3. FoldedWordGraph

The central data model. For a word like **كاتِب** (writer), the graph contains:

- **Nodes**: word, root (ktb), pattern (faail), agency-pole, causation-pole, etc.
- **Edges** (12 types): `has_root`, `has_pattern`, `folds_agency`, `folds_patienthood`, `folds_causation`, `folds_instrument`, `folds_time`, `folds_place`, `folds_nisba`, `folds_comparison`, `folds_multiplication`, `folds_transformation`
- **Semantic vectors**: `role_vector`, `domain_vector`, `event_vector`

### 4. ConceptCenter (مركز المفهوم)

A 17-axis representation capturing:

`essence`, `event`, `attribute`, `agency`, `patienthood`, `causation`, `instrument`, `time_place`, `nisba`, `comparison`, `plurality`, `context`, `evidence`, `certainty`

Each axis is a dict of float scores (0–1).

### 5. Qiyasi / Samai / Shadh Classification

Arabic morphology distinguishes:

- **قياسي (qiyasi)** — derived by analogy from a productive rule (high certainty)
- **سَماعي (samai)** — heard from native speakers; not fully rule-governed (medium certainty)
- **شاذّ (shadh)** — exceptional; violates normal patterns (lower certainty)

The `PatternCertaintyScorer` assigns certainty scores based on this classification.

---

## CLI Commands

### `morph-analyze`

Full morphosemantic analysis of an Arabic word.

```bash
python -m mcd.cli morph-analyze --word "كاتِب" --output json
python -m mcd.cli morph-analyze --word "استخرج" --output markdown
python -m mcd.cli morph-analyze --word "زارِع" --output text
```

### `morph-unfold`

Unfolds the FoldedWordGraph into a layered Markdown table.

```bash
python -m mcd.cli morph-unfold --word "مَكتَبة" --output markdown
python -m mcd.cli morph-unfold --word "عُلَماء" --output json
```

### `concept-center`

Computes the 17-axis ConceptCenter for a word.

```bash
python -m mcd.cli concept-center --word "زِراعة" --output json
python -m mcd.cli concept-center --word "صانِع" --output text
```

### `pattern-operator`

Looks up a morphological pattern operator.

```bash
python -m mcd.cli pattern-operator --pattern-id faail --output json
python -m mcd.cli pattern-operator --pattern-form "مَفعول" --output markdown
```

### `root-family`

Shows the complete morphosemantic family of an Arabic root.

```bash
python -m mcd.cli root-family --root-id ktb --output text
python -m mcd.cli root-family --root-id zraa --output json
```

---

## Python API

```python
from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker

linker = MorphosemanticTraceLinker()
bundle = linker.link("كاتِب")

# Access the folded word graph
graph = bundle.folded_word_graph
print(graph.selected_root)    # "ktb"
print(graph.selected_pattern) # "faail"

# Access the concept center
cc = bundle.concept_center
print(cc.root_family)    # "ktb"
print(cc.agency_axis)    # {"agency": 1.0, ...}

# Unfold to Markdown
from mcd.morphosemantics.folded_word_unfolder import FoldedWordUnfolder
unfolder = FoldedWordUnfolder()
unfolded = unfolder.unfold(graph)
print(unfolded.to_markdown())

# Root family
from mcd.morphosemantics.root_family_graph import RootFamilyGraphBuilder
builder = RootFamilyGraphBuilder()
family = builder.build("ktb")
for member in family.members:
    print(f"{member.word}: {member.role}")
```

---

## Data Files

All data lives in `data/morphosemantics/`. Files are optional — every engine includes built-in hardcoded data that is used when files are absent.

| File | Format | Records |
|------|--------|---------|
| `root_ontology_seed_ar.jsonl` | JSONL | 50 roots |
| `pattern_operator_registry.json` | JSON | 17 patterns |
| `masdar_event_classes.json` | JSON | 10 masdars |
| `jamid_essence_seed_ar.jsonl` | JSONL | 50 essences |
| `nisba_patterns.json` | JSON | 8 nisba forms |
| `diminutive_patterns.json` | JSON | 8 diminutives |
| `broken_plural_patterns.json` | JSON | 30 plural pairs |
| `qiyasi_samai_shadh_seed.jsonl` | JSONL | 50 entries |
| `contextual_pattern_examples_ar.jsonl` | JSONL | 50 examples |
| `folded_word_golden_examples_ar.jsonl` | JSONL | 30 golden tests |

---

## Extending the Engine

### Adding a new root

Append a line to `data/morphosemantics/root_ontology_seed_ar.jsonl`:

```json
{"root_id": "shr", "radicals": ["ش", "ه", "ر"], "root_type": "triliteral", "semantic_core": "الشهرة والشهر", "sensory_domains": ["اجتماعي", "زمني"], "event_potential": ["شهرة", "تشهير"], "transitivity_potential": "both", "causation_potential": 0.4, "metaphor_potential": 0.7, "examples": ["اشتَهَرَ", "مَشهور", "شَهير"], "certainty": 0.95}
```

### Adding a new pattern

Add an entry to `data/morphosemantics/pattern_operator_registry.json`:

```json
{
  "pattern_id": "mif3aal_instrument",
  "pattern_form": "مِفعال",
  "family": "instrument_noun",
  "operator_vector": {"agency": 0.0, "instrument": 1.0, "patienthood": 0.2, ...},
  "examples": ["مِفتاح", "مِنشار"],
  "certainty_policy": "samai"
}
```

### Registering an ambiguous word

Extend `contextual_pattern_resolver.py` → `_AMBIGUOUS` dict with candidates:

```python
"سلم": [
    {"meaning": "ladder", "domain": "physical", "required_context": ["صَعَدَ", "نَزَلَ"]},
    {"meaning": "peace", "domain": "social", "required_context": ["اتِّفاق", "سَلام"]},
]
```

---

## Testing

```bash
PYTHONPATH=src python -m pytest tests/test_morphosemantics.py -v
```

22 tests covering all major subsystems. All tests are self-contained and require no data files.

---

## Design Principles

1. **No external dependencies** — pure Python, no network calls, no ML inference
2. **Graceful degradation** — all loaders return empty/generic results on file errors
3. **Built-in data** — every engine has hardcoded seed data so it works out of the box
4. **Dataclass-first** — all data structures are `@dataclass` with `to_dict()` / `from_dict()`
5. **`from __future__ import annotations`** — used throughout for forward references
6. **Certainty-aware** — every analysis carries an explicit certainty score
7. **Arabic-first** — Arabic text is stored natively (UTF-8), not transliterated in outputs
