# Curriculum Mathematical Hardening — Phase 5.3.1

## Summary

Phase 5.3.1 expands and hardens the cognitive curriculum from 8 levels (400 examples) to 10 levels (1000+ examples) with full mathematical contract validation.

## Changes

### Data Expansion
| Level | Name | Examples |
|-------|------|---------|
| 1–8 | Existing levels | 100 each (was 50) |
| 9 | domain_reasoning | 100 new |
| 10 | graph_vector_composition | 100+ new |
| — | Golden examples | 50 |
| — | Adversarial examples | 200 |

### Schema Updates
- `VALID_LEVELS`: 1–10 (was 1–8)
- `VALID_TARGET_LAYERS`: added `domain_reasoning`, `graph_vector_composition`
- `VALID_CERTAINTY_POLICIES`: added `strong_knowledge`, `hypothesis`

### Scoring Changes (`_score_unit`)
- Level-aware base scores (level 1 = 0.7, level 8 = 0.3)
- Levels 7–8 missing `evidence_need` → score = 0.0
- Level 4 missing `relations` → penalised

### Coverage Denominators
- Level coverage: `/10` (was `/8`)
- Layer coverage: `/14` (was `/12`)

### New CLI Commands
```bash
python -m mcd curriculum-contract-check --profile full_curriculum
python -m mcd curriculum-qualification --profile full_curriculum_extended
```

### New Profiles
- `adversarial`: levels=[8]
- `full_curriculum_extended`: levels=[1..10]

## Qualification Gate

Run `curriculum-qualification` to check all dimensions against thresholds before API deployment.
