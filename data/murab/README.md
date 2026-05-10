# data/murab — Arabic Mu'rab / I'rab Data Files

This directory contains structured data for the Arabic I'rab (Mu'rab) relational engineering layer.

## JSON Registry Files

| File | Description |
|------|-------------|
| `irab_case_registry.json` | Six I'rab case definitions (nominative, accusative, genitive, jussive, indeclinable_local, unknown) |
| `irab_marker_registry.json` | 15 I'rab marker entries with Unicode symbols |
| `governing_factors_ar.json` | ≥20 governing factor objects (prepositions, inna/kana particles, jussive/nasb particles) |

## JSONL Example Files

| File | Count | Description |
|------|-------|-------------|
| `nominative_examples_ar.jsonl` | 100 | Nominative case examples |
| `accusative_examples_ar.jsonl` | 150 | Accusative case examples |
| `genitive_examples_ar.jsonl` | 100 | Genitive case examples |
| `jussive_examples_ar.jsonl` | 80 | Jussive examples (lam, lamma, la nahy) |
| `idafa_examples_ar.jsonl` | 100 | Idafa (إضافة) construction examples |
| `tawabi_examples_ar.jsonl` | 100 | Tawabi' (توابع) agreement examples |
| `hal_tamyiz_examples_ar.jsonl` | 80 | Hal (حال) and Tamyiz (تمييز) disambiguation |
| `zarf_examples_ar.jsonl` | 80 | Zarf (ظرف) time/place adverbials |
| `estimated_irab_examples_ar.jsonl` | 80 | Estimated I'rab (مقصور / منقوص / مضاف إلى ياء) |
| `irregular_irab_examples_ar.jsonl` | 5+ | Irregular I'rab (five nouns, dual, plurals) |
| `murab_golden_examples_ar.jsonl` | 100 | Golden standard annotated examples |
| `murab_adversarial_examples_ar.jsonl` | 100 | Adversarial/tricky cases |

## JSONL Format

Each line is a JSON object with at least:
```json
{
  "example_id": "nom_001",
  "text": "جاء المعلمُ",
  "tokens": [{"token": "...", "role": "...", "case": "..."}],
  "notes": "الفاعل مرفوع"
}
```
