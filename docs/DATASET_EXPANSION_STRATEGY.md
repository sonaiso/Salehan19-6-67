# Dataset Expansion Strategy — MCD Phase 4

## Overview

Phase 4 introduces a comprehensive dynamic dataset expansion framework for the MCD (Minimal Cognitive Decoder) project. The strategy focuses on building a high-coverage, multi-dimensional benchmark dataset for Arabic-language epistemic evaluation.

## Goals

1. **Coverage**: Achieve ≥0.80 coverage score across all evaluation dimensions
2. **Balance**: Cover all 10 judgment types, 4 difficulties, 5 certainty policies
3. **Robustness**: Include adversarial examples to test model edge cases
4. **Scalability**: Support dynamic generation via templates

## Dataset Architecture

### Static Gold Dataset (350 examples)
Curated, human-verified examples across 12 categories:
- Epistemic (40), Technical (30), Practical (30), Value (30)
- Shari (35), Linguistic (35), Ambiguous (30), Analogy (30)
- Metaphor (25), Usuli (25), Civilization (20), Society (20)

### Dynamic Generation
Templates allow generation of thousands of examples from 10 template families.
Each template family covers a distinct judgment type.

### Adversarial Examples (50+)
Five adversarial categories testing model robustness:
- **ADV-FC**: False certainty traps
- **ADV-HH**: Harm-haram conflation
- **ADV-AN**: Analogy without illah
- **ADV-ML**: Metaphor literalization
- **ADV-OE**: Opinion as evidence

### Ambiguity Examples (30+)
Arabic words with multiple meanings requiring context for disambiguation.

### Calibration Examples (31)
Examples targeting specific calibration dimensions for measurement.

## Coverage Requirements

| Dimension | Required | Strategy |
|-----------|----------|----------|
| Judgment Types | All 10 | Separate categories per type |
| Difficulties | All 4 | easy/medium in static, hard in shari/usuli, adversarial in adversarial set |
| Certainty Policies | All 5 | static_gold covers strong/probable/hypothesis/suspend; calibration adds near_certainty |
| Source Types | 4/5 static | dynamic_generated via generator only |

## Key Principles

1. **Shari examples always suspend** — no exceptions
2. **Ambiguous examples always require_context** — cannot be resolved without more input
3. **Adversarial examples expose false certainty** — model must resist overconfidence
4. **Coverage score ≥ 0.80** is the minimum threshold for production readiness
