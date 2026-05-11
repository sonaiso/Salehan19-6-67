# data/evaluation — MCD Phase 4 Benchmark Dataset

This directory contains the benchmark dataset for Phase 4 dynamic dataset expansion.

## Files

| File | Description | Count |
|------|-------------|-------|
| `static_gold_ar.jsonl` | Curated gold-standard Arabic examples | 350 |
| `adversarial_ar.jsonl` | Adversarial examples testing model robustness | 100 |
| `ambiguity_ar.jsonl` | Ambiguous Arabic words/phrases | 60 |
| `calibration_ar.jsonl` | Calibration examples per dimension | 61 |
| `dynamic_templates_ar.json` | Templates for dynamic dataset generation | 10 families |
| `benchmark_profiles.json` | Named benchmark profiles | 5 profiles |
| `web_evaluator_prompts_ar_dataset.jsonl` | Web Evaluator Arabic Prompt Dataset (Categories A–I) | 85 |

## Categories in static_gold_ar.jsonl

- **SG-EP**: Epistemic (physical/empirical claims)
- **SG-TC**: Technical (how-to and procedural)
- **SG-PR**: Practical (step-by-step processes)
- **SG-VL**: Value (ethical/normative claims)
- **SG-SH**: Shari (Islamic rulings — always suspend)
- **SG-LG**: Linguistic (language analysis)
- **SG-AM**: Ambiguous (context-dependent words)
- **SG-AN**: Analogy (analogical reasoning)
- **SG-MT**: Metaphor (figurative expressions)
- **SG-US**: Usuli (usul al-fiqh concepts)
- **SG-CV**: Civilization (civilizational concepts)
- **SG-SC**: Society (social phenomena)

## Web Evaluator Dataset (WEB-001 – WEB-085)

Nine categories of Arabic prompts with richer grounding metadata:

| Category | IDs | Topic |
|----------|-----|-------|
| A | WEB-001–005 | Reality grounding / Epistemic |
| B | WEB-006–015 | Ambiguity (single words without context) |
| C | WEB-016–025 | Harm vs Haram / Values vs Shari |
| D | WEB-026–035 | Technical / Practical |
| E | WEB-036–045 | Analogy / Illah (علة) |
| F | WEB-046–055 | Civilization vs Civility |
| G | WEB-056–065 | Society / Public Opinion |
| H | WEB-066–075 | Linguistic / Usuli |
| I | WEB-076–085 | Adversarial false evidence / false certainty |

### Schema fields (WebEvaluatorExample)

- `id` — WEB-NNN identifier
- `prompt` — the Arabic input
- `what_is_reality` — description of the grounded reality behind the prompt
- `root_domain`, `concept_type`, `knowledge_category`, `judgment_type`, `evidence_need` — lists of taxonomy labels
- `certainty_policy` — expected certainty decision
- `expected_status` — expected epistemic status
- `required_behavior` — expected system response behavior
- `required_warnings` — warnings that must be raised
- `forbidden_outputs` — outputs that must be avoided
- `scoring_focus` — evaluation dimensions to emphasize
- `difficulty` — easy / medium / hard / adversarial
- `tags` — free-form classification tags

## Adversarial Categories

- **ADV-FC**: False certainty traps
- **ADV-HH**: Harm-haram conflation
- **ADV-AN**: Analogy without illah
- **ADV-ML**: Metaphor literalization
- **ADV-OE**: Opinion as evidence

## Benchmark Profiles

- `quick`: 50 easy/medium static_gold examples
- `standard`: 300 static_gold + dynamic examples
- `full`: 1000 all sources
- `adversarial`: 200 adversarial-only examples
- `gpt55_simulation`: 50 epistemic/shari/ambiguous examples

## Coverage Requirements

The full dataset (all 4 JSONL files combined) must cover:
- All 10 judgment types
- All 4 difficulties (easy, medium, hard, adversarial)
- All 5 certainty policies
- All 5 source types (static_gold, adversarial, ambiguity, calibration + dynamic_generated from generator)
