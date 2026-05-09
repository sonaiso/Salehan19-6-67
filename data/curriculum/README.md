# Curriculum Data Directory

This directory contains the Phase 5.3 Cognitive Curriculum Learning dataset for the Reasoning Mind.

## Structure

Each file contains 50 JSONL examples at a specific cognitive level:

| File | Level | Layer | Description |
|------|-------|-------|-------------|
| `level_01_things_ar.jsonl` | 1 | thing | Basic thing identification |
| `level_02_properties_ar.jsonl` | 2 | property | Entity–property mapping |
| `level_03_actions_ar.jsonl` | 3 | action | Agent–action–patient triples |
| `level_04_relations_ar.jsonl` | 4 | relation | Semantic relation triples |
| `level_05_causes_effects_ar.jsonl` | 5 | cause/effect | Causal reasoning |
| `level_06_instruments_times_places_ar.jsonl` | 6 | instrument/time/place | Contextual grounding |
| `level_07_evidence_certainty_ar.jsonl` | 7 | evidence/certainty | Epistemic discipline |
| `level_08_mixed_reasoning_ar.jsonl` | 8 | mixed_reasoning | Adversarial scenarios |

## Schema

Each JSONL line follows the `CognitiveUnit` schema:
```json
{
  "unit_id": "L01-0001",
  "input_text": "النار شيء.",
  "level": 1,
  "target_layer": "thing",
  "expected_frame": { ... },
  "expected_warnings": [],
  "forbidden_confusions": [],
  "evidence_need": [],
  "certainty_policy": "certain_knowledge",
  "difficulty": "easy",
  "tags": ["things"],
  "metadata": {}
}
```

## Usage

```python
from mcd.curriculum import CurriculumDataset
ds = CurriculumDataset()
units = ds.load_all()  # 400 units
level7 = ds.load_level(7)  # 50 units
```
