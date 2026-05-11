# Arabic Mu'rab / I'rab Relational Engineering Layer

**Phase 7.5** — MCD (Morpho-Conceptual Decoder) relational layer for Arabic grammatical case analysis (الإعراب).

## Overview

The Mu'rab layer analyzes Arabic I'rab (grammatical case inflection), resolving case markers, governing factors, syntactic roles, and semantic projections for each token in an Arabic sentence.

## Architecture

```
src/mcd/murab/
├── __init__.py                  # Package exports
├── murab_schema.py              # MurabUnit dataclass
├── irab_case.py                 # IrabCase + registry loader
├── irab_marker.py               # IrabMarker + registry loader
├── governing_factor.py          # GoverningFactor detection
├── case_resolver.py             # Main CaseResolver orchestrator
├── syntactic_role_resolver.py   # Context-aware syntactic role
├── nominative_resolver.py       # Nominative (رفع) rules
├── accusative_resolver.py       # Accusative (نصب) rules
├── genitive_resolver.py         # Genitive (جر) rules
├── jussive_resolver.py          # Jussive (جزم) rules
├── mood_resolver.py             # Imperfect verb mood
├── agreement_engine.py          # Case agreement checking
├── dependency_resolver.py       # Dependency relations
├── idafa_engine.py              # Idafa (إضافة) detection
├── tawabi_engine.py             # Tawabi' (توابع) agreement
├── hal_tamyiz_engine.py         # Hal/Tamyiz disambiguation
├── zarf_engine.py               # Zarf (ظرف) adverbials
├── exception_irab_engine.py     # Exception (استثناء) cases
├── estimated_irab_engine.py     # Estimated I'rab (مقصور/منقوص)
├── irregular_irab_registry.py   # Irregular patterns (خمسة أسماء)
├── murab_graph_builder.py       # Relational graph construction
├── murab_trace_linker.py        # Unicode trace chain
├── murab_certainty_policy.py    # Certainty evaluation
├── murab_report.py              # Report generation
└── serializers.py               # JSON/Markdown serialization
```

## I'rab Cases

| Case | Arabic | Grammatical Function | Default Marker |
|------|--------|----------------------|----------------|
| `nominative` | الرفع | Raising (رفع) | Damma (ُ) |
| `accusative` | النصب | Accusation (نصب) | Fatha (َ) |
| `genitive` | الجر | Lowering (جر) | Kasra (ِ) |
| `jussive` | الجزم | Jussive (جزم) | Sukun (ْ) |
| `indeclinable_local` | البناء المحلي | Local position | — |
| `unknown` | مجهول | Undetermined | — |

## Governing Factors

| Factor | Arabic | Governs | Example |
|--------|--------|---------|---------|
| Prepositions (في/من/إلى) | حروف الجر | genitive | في المدرسةِ |
| Inna particles (إن/أن/لكن) | إن وأخواتها | accusative (name) | إنَّ العلمَ |
| Kana verbs (كان/أصبح) | كان وأخواتها | nominative (name) | كانَ زيدٌ |
| Lam/Lamma (لم/لما) | حروف الجزم | jussive | لم يذهبْ |
| Lan/An (لن/أن) | حروف النصب | accusative mood | لن يذهبَ |
| Idafa structure | الإضافة | genitive (mudaf ilayh) | كتابُ الطالبِ |

## Certainty Model

I'rab analysis raises **syntactic certainty only**, never factual/world-knowledge certainty:

```
evidence_effect = "syntactic_only"  # Always
```

| Condition | Syntactic Certainty |
|-----------|---------------------|
| Apparent marker + clear governing factor | 0.9 |
| Apparent marker, no factor | 0.75 |
| Estimated marker + clear factor | 0.7 |
| Unclear factor | 0.5 |
| Unknown case | 0.4 |

## Irregular I'rab

### الأسماء الخمسة (Five Nouns)

| Word | Nominative | Accusative | Genitive |
|------|-----------|------------|---------|
| أب (father) | أبو (waw) | أبا (alif) | أبي (ya) |
| أخ (brother) | أخو (waw) | أخا (alif) | أخي (ya) |
| حم (father-in-law) | حمو (waw) | حما (alif) | حمي (ya) |
| فم (mouth) | فو (waw) | فا (alif) | في (ya) |
| ذو (possessor) | ذو (waw) | ذا (alif) | ذي (ya) |

### Dual — المثنى
- Nominative: ألف (ـان) e.g. طالبان
- Accusative/Genitive: ياء (ـين) e.g. طالبين

### Sound Masculine Plural — جمع المذكر السالم
- Nominative: واو (ـون) e.g. معلمون
- Accusative/Genitive: ياء (ـين) e.g. معلمين

## Estimated I'rab — الإعراب التقديري

| Pattern | Example | Rule |
|---------|---------|------|
| مقصور (ends in ى) | الفتى | Damma/Fatha/Kasra all estimated |
| منقوص (ends in ي) | القاضي | Damma/Kasra estimated |
| مضاف إلى ياء المتكلم | كتابي | All case markers estimated |

## CLI Usage

```bash
# Analyze full sentence
python -m mcd.cli murab-analyze --text "جاء المعلمُ" --output json

# Resolve single token
python -m mcd.cli irab-resolve --token "الكتابُ" --output text

# Build relational graph
python -m mcd.cli murab-graph --text "ذهبَ الطالبُ إلى المدرسةِ" --output json

# Evaluate certainty
python -m mcd.cli irab-certainty --token "المدرسةِ" --context "في المدرسةِ" --output json

# Show Unicode trace chain
python -m mcd.cli murab-trace --token "أب" --output json
```

## Key Linguistic Distinctions

### Mubtada is Nominative but NOT Agent
```
زيدٌ ذكيٌّ   → زيد is nominative (mubtada/subject) but NOT an agent
```

### Hal and Tamyiz are Accusative but NOT Objects
```
جاء فرحاً    → فرحاً is accusative (hal) — NOT a direct object
عشرون كتاباً → كتاباً is accusative (tamyiz) — NOT a direct object
```

### Idafa Does Not Always Mean Ownership
```
خاتمُ ذهبٍ  → specification (made of gold), not ownership
بناءُ المصنع → action/masdar relationship
```

### Lam vs Lan
```
لم يذهبْ   → jussive (sukun marker) — negation of past
لن يذهبَ   → accusative mood (fatha marker) — negation of future
```

## Data Files

All training/example data lives in `data/murab/`. See `data/murab/README.md` for details.

## Running Tests

```bash
PYTHONPATH=src python -m pytest tests/test_murab*.py tests/test_irab*.py tests/test_governing*.py tests/test_nominative*.py tests/test_accusative*.py tests/test_genitive*.py tests/test_jussive*.py tests/test_mood*.py tests/test_idafa*.py tests/test_tawabi*.py tests/test_hal_tamyiz*.py tests/test_zarf*.py tests/test_estimated*.py tests/test_irregular*.py -v
```
