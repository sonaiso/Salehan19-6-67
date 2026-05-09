# Dynamic Benchmarking — MCD Phase 4

## Overview

Dynamic benchmarking enables generation of unlimited evaluation examples from a compact set of templates. This approach complements the static gold dataset with scalable, reproducible test generation.

## Components

### DynamicDatasetGenerator
- Loads templates from `data/evaluation/dynamic_templates_ar.json`
- Expands templates with variable substitution
- Generates `BenchmarkExample` objects with source_type="dynamic_generated"
- Supports seeded random for reproducibility

### Template Format
```json
{
  "template_id": "TMPL-CATEGORY-NNN",
  "template": "هل {action} حرام؟",
  "variables": {"action": ["الكذب", "الغش", ...]},
  "expected": {
    "certainty_policy": "suspend",
    "judgment_types": {"shari": 0.9},
    ...
  }
}
```

### Benchmark Profiles
Named profiles control which examples are used for evaluation:

| Profile | Count | Description |
|---------|-------|-------------|
| `quick` | 50 | Fast smoke test |
| `standard` | 300 | Standard evaluation |
| `full` | 1000 | Complete benchmark |
| `adversarial` | 200 | Robustness testing |
| `gpt55_simulation` | 50 | GPT-5.5 comparison |

## CLI Usage

```bash
# Generate dataset
PYTHONPATH=src python -m mcd generate-dataset --profile standard --count 100

# Check coverage
PYTHONPATH=src python -m mcd dataset-coverage

# Validate dataset
PYTHONPATH=src python -m mcd validate-dataset

# Generate report
PYTHONPATH=src python -m mcd dataset-report

# Calibrate certainty
PYTHONPATH=src python -m mcd calibrate-certainty --profile quick
```

## Coverage Matrix

The `CoverageMatrix` class measures four dimensions:
1. **judgment_type**: 10 expected types (epistemic, technical, value, shari, practical, linguistic, ambiguous, analogy, metaphor, usuli)
2. **difficulty**: 4 levels (easy, medium, hard, adversarial)
3. **certainty_policy**: 5 policies (near_certainty, strong_knowledge, probable_knowledge, hypothesis, suspend)
4. **source_type**: 5 types (static_gold, dynamic_generated, adversarial, ambiguity, calibration)

Target: **≥ 0.80 overall coverage score**

## Dataset Splits

Use `split_dataset()` to divide examples into:
- **train_calibration** (60%): For training calibration models
- **validation** (20%): For hyperparameter tuning
- **holdout** (20%): For final evaluation

Splits are stratified by source_type to ensure balance.
