# data/murab — Arabic Mu'rab/I'rab Relational Data

Phase 7.5 seed data for the Arabic I'rab Relational Engineering Layer.

## Files

| File | Format | Lines | Description |
|------|--------|-------|-------------|
| `irab_case_registry.json` | JSON | 6 cases | الحالات الإعرابية الست |
| `irab_marker_registry.json` | JSON | 12 markers | علامات الإعراب |
| `governing_factors_ar.json` | JSON | 16 factors | العوامل النحوية |
| `nominative_examples_ar.jsonl` | JSONL | 100 | أمثلة الرفع |
| `accusative_examples_ar.jsonl` | JSONL | 150 | أمثلة النصب |
| `genitive_examples_ar.jsonl` | JSONL | 100 | أمثلة الجر |
| `jussive_examples_ar.jsonl` | JSONL | 80 | أمثلة الجزم |
| `idafa_examples_ar.jsonl` | JSONL | 100 | أمثلة الإضافة |
| `tawabi_examples_ar.jsonl` | JSONL | 100 | أمثلة التوابع |
| `hal_tamyiz_examples_ar.jsonl` | JSONL | 80 | أمثلة الحال والتمييز |
| `zarf_examples_ar.jsonl` | JSONL | 80 | أمثلة الظرف |
| `estimated_irab_examples_ar.jsonl` | JSONL | 80 | أمثلة الإعراب المقدر |
| `irregular_irab_examples_ar.jsonl` | JSONL | ~91 | أمثلة الإعراب الشاذ |
| `murab_golden_examples_ar.jsonl` | JSONL | 100 | أمثلة ذهبية متكاملة |
| `murab_adversarial_examples_ar.jsonl` | JSONL | 100 | أمثلة خادعة |

## JSONL Schema

### Example entry (nominative)
```json
{"id": "nom-001", "sentence": "جاءَ زيدٌ", "word": "زيدٌ",
 "irab_case": "nominative", "syntactic_role": "فاعل",
 "semantic_role": "agent", "governing_factor": "فعل جاء"}
```

### Golden example entry
```json
{"id": "golden-001", "sentence": "كَتَبَ زيدٌ الدَّرسَ", "analysis": [
  {"word": "زيدٌ", "irab_case": "nominative", "irab_marker": "damma",
   "syntactic_role": "فاعل", "semantic_role": "agent"}
]}
```

## Key Principles

1. **الرفع ≠ الفاعلية**: Not every nominative word is an agent.
2. **النصب ≠ المفعولية**: Not every accusative word is a patient.
3. **الجر بالإضافة ≠ الملكية**: Genitive via idafa ≠ ownership.
4. **يقين نحوي ≠ يقين واقعي**: Syntactic certainty ≠ factual certainty.
