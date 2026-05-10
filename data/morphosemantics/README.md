# Data — Arabic Morphosemantic Fractal Engine

This directory contains seed data files for Phase 7.3: Arabic Morphosemantic Fractal Engine.

All data files are loaded at runtime with graceful fallback to built-in hardcoded data when
files are absent or malformed.  Data files **extend** the built-in data rather than replacing it.

## Files

| File | Format | Description |
|------|--------|-------------|
| `root_ontology_seed_ar.jsonl` | JSONL | 102 Arabic triconsonantal root entries with semantic metadata |
| `pattern_operator_registry.json` | JSON | 17 morphological pattern operators with semantic operator vectors |
| `masdar_event_classes.json` | JSON | 10 masdar (verbal noun) event class definitions |
| `jamid_essence_seed_ar.jsonl` | JSONL | 101 jamid (non-derived) essence terms |
| `nisba_patterns.json` | JSON | 8 nisba (relational adjective) derivation patterns |
| `diminutive_patterns.json` | JSON | 8 diminutive (تصغير) form entries |
| `broken_plural_patterns.json` | JSON | 30 broken plural (جمع التكسير) form pairs |
| `qiyasi_samai_shadh_seed.jsonl` | JSONL | 101 entries classified as analogical (قياسي), heard (سَماعي), or exceptional (شاذّ) |
| `contextual_pattern_examples_ar.jsonl` | JSONL | 100 contextual disambiguation examples |
| `folded_word_golden_examples_ar.jsonl` | JSONL | 60 golden test examples for folded word graph validation |

## Data Schema

### JSONL Files
Each line is a self-contained JSON object.  Empty lines are ignored.

### root_ontology_seed_ar.jsonl fields
- `root_id` — unique identifier (ASCII transliteration)
- `radicals` — list of 3 Arabic consonants
- `root_type` — `triliteral | hollow | defective | doubled | hamzated | assimilated`
- `semantic_core` — Arabic description of core meaning
- `sensory_domains` — list of sensory/cognitive domain tags
- `event_potential` — list of event types the root can express
- `transitivity_potential` — `transitive | intransitive | both`
- `causation_potential` — float 0–1
- `metaphor_potential` — float 0–1
- `examples` — sample derived words
- `certainty` — confidence in this entry (0–1)

### pattern_operator_registry.json fields
- `pattern_id` — unique identifier
- `pattern_form` — Arabic pattern form
- `family` — semantic family of pattern
- `operator_vector` — dict of 12 semantic dimension scores (0–1)
- `examples` — example words fitting the pattern
- `certainty_policy` — `high | medium | low`

## Extending Data
To add custom roots, append JSONL lines to the `.jsonl` files.
To add custom patterns, add entries to the `patterns` array in `pattern_operator_registry.json`.

All loaders perform de-duplication by ID — later entries with the same ID override earlier ones.
