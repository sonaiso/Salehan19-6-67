# data/evaluation — MCD Phase 4 Benchmark Dataset

This directory contains the benchmark dataset for Phase 4 dynamic dataset expansion.

## Files

| File | Description | Count |
|------|-------------|-------|
| `static_gold_ar.jsonl` | Curated gold-standard Arabic examples | 350 |
| `adversarial_ar.jsonl` | Adversarial examples testing model robustness | 50+ |
| `ambiguity_ar.jsonl` | Ambiguous Arabic words/phrases | 30+ |
| `calibration_ar.jsonl` | Calibration examples per dimension | 30+ |
| `dynamic_templates_ar.json` | Templates for dynamic dataset generation | 10 families |
| `benchmark_profiles.json` | Named benchmark profiles | 5 profiles |

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
