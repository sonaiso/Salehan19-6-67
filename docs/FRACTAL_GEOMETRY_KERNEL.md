# Fractal Geometry Kernel — Phase 7.0K
# النواة الهندسية الكسورية — المرحلة 7.0K

## Overview | نظرة عامة

The **Fractal Geometry Kernel** (Phase 7.0K) is the foundational mathematical and epistemic layer of the Minimal Cognitive Decoder (MCD). It provides a unified framework for representing, validating, and reasoning over all linguistic and cognitive units across multiple abstraction levels — from Unicode codepoints up to proof objects.

**النواة الهندسية الكسورية** هي الطبقة الرياضية والمعرفية الأساسية لنظام فك التشفير المعرفي الأدنى (MCD). توفر إطاراً موحداً لتمثيل وتحقق والاستدلال على جميع الوحدات اللغوية والمعرفية عبر مستويات تجريد متعددة — من نقاط يونيكود حتى كائنات البرهان.

---

## Core Laws | القوانين الأساسية

### Law 1: Trace Preservation | قانون الحفاظ على الأثر
Every fold operation must carry at least one `trace_ref`. Folding without a trace is a hard violation.

كل عملية طي يجب أن تحمل مرجع أثر واحداً على الأقل. الطي بلا أثر انتهاك صريح.

### Law 2: Evidence Preservation | قانون الحفاظ على الدليل
If a unit requires evidence, that requirement must be carried through any fold operation.

إذا كانت وحدة تتطلب دليلاً، يجب أن تُحمل هذه الضرورة عبر أي عملية طي.

### Law 3: Certainty Non-Increase | قانون عدم زيادة اليقين
Folding **cannot** increase certainty. `post_certainty ≤ pre_certainty`.

الطي **لا يمكنه** زيادة اليقين. اليقين بعد الطي ≤ اليقين قبله.

### Law 4: Refold Consistency | قانون اتساق إعادة الطي
Re-folding the same input must produce equivalent preserved relations and vectors.

إعادة طي نفس المدخل يجب أن تنتج علاقات ومتجهات محفوظة مكافئة.

### Law 5: No Proof from Fold Alone | قانون عدم البرهان من الطي وحده
A `Certificate` proof status cannot arise from fold operations alone — independent evidence is required.

لا يمكن أن ينشأ برهان من درجة `Certificate` من عمليات الطي وحدها — يُشترط دليل مستقل.

---

## Invariants | الثوابت

| Invariant | Description (EN) | الوصف (AR) |
|-----------|-----------------|------------|
| `emphasis_not_evidence` | Emphasis (Mabni) ≠ Evidence | التوكيد ≠ دليل |
| `irab_not_factual_certainty` | I'rab (syntactic) ≠ Factual certainty | الإعراب ≠ يقين حقيقي |
| `gpt_not_evidence` | GPT output is never evidence | مخرجات GPT ليست دليلاً |
| `trace_not_truth` | Trace completeness ≠ truth | اكتمال الأثر ≠ صحة |
| `fold_does_not_raise_certainty` | Fold ≠ certainty increase | الطي لا يرفع اليقين |
| `no_proof_from_fold_alone` | Proof requires independent evidence | البرهان يستلزم دليلاً مستقلاً |

---

## Architecture | البنية

```
fractal_kernel/
├── fractal_unit.py           # CognitiveFractalUnit — base unit across all levels
├── level_morphism.py         # LevelMorphism + LevelMorphismRegistry
├── vector_space_registry.py  # VectorDimension, UnifiedVector, UnifiedVectorSpaceRegistry
├── operator_algebra.py       # CognitiveOperator + OperatorAlgebra
├── fold_laws.py              # FoldOperation, UnfoldOperation, RefoldCheck, FoldLawEnforcer
├── conflict_resolver.py      # CrossLayerConflict + CrossLayerConflictResolver
├── concept_center_memory.py  # ConceptCenterRecord + ConceptCenterMemory
├── pattern_memory.py         # FractalPattern + PatternMemory
├── proof_object.py           # ProofObject (certificate/hypothesis/zero)
├── reverse_trace.py          # ReverseTrace — backward audit chain
├── jami_mani_metrics.py      # JamiManiReport + JamiManiCalculator
├── residual_folding_contract.py  # GPTResidualFoldingContract
├── kernel_validator.py       # KernelValidator + KernelValidationReport
├── kernel_report.py          # KernelReport — markdown/json output
├── serializers.py            # to_json() utility
└── __init__.py               # Public exports
```

---

## Levels | المستويات

| Level | Description |
|-------|-------------|
| `unicode` | Raw Unicode codepoint |
| `grapheme` | Grapheme cluster |
| `token` | Tokenized surface form |
| `root` | Arabic morphological root |
| `pattern` | Arabic morphological pattern |
| `word` | Full word form |
| `mabni` | Logical-pragmatic operator (Mabni) |
| `murab` | I'rab relational unit (Mu'rab) |
| `phrase` | Phrasal unit |
| `sentence` | Sentence level |
| `concept` | Concept center node |
| `judgment` | Epistemic judgment |
| `proof` | Proof object |
| `residual` | GPT residual / unresolved gap |
| `fold_pattern` | Folded memory pattern |

---

## Vector Dimensions | أبعاد المتجه

The kernel defines 15 canonical dimensions:

- `role_vector` — Semantic role weight
- `domain_vector` — Domain relevance
- `operator_vector` — Operator strength
- `evidence_vector` — Evidence weight (requires trace)
- `certainty_vector` — Overall certainty
- `trace_vector` — Traceability score (requires trace)
- `proof_vector` — Proof confidence (requires trace)
- `residual_vector` — GPT residual magnitude
- `pragmatic_vector` — Pragmatic force
- `irab_vector` — I'rab/syntactic position
- `morphosemantic_vector` — Morphosemantic weight
- `syntactic_certainty` — Syntactic position certainty
- `factual_certainty` — Factual/empirical certainty (requires trace)
- `evidence_creation` — Evidence creation capacity (requires trace)
- `discourse_force` — Discourse/emphasis force

**Critical constraints:**
- `evidence_creation` cannot be raised by `MabniOperator` without trace evidence
- `factual_certainty` cannot be raised by `IrabOperator` without independent evidence

---

## Proof Object States | حالات كائن البرهان

| Status | Meaning |
|--------|---------|
| `zero` | No proof attempted |
| `hypothesis` | Working hypothesis, no certificate |
| `certificate` | Full proof: requires `evidence_refs`, no `blockers`, and a `reverse_trace_id` |

---

## CLI Commands | أوامر سطر الأوامر

```bash
# Validate kernel with a sample unit
python -m mcd.cli kernel-validate --output json

# Generate markdown report
python -m mcd.cli kernel-report --output markdown

# Demo fold operation
python -m mcd.cli kernel-demo-fold --text "النموذج قال إن كل الشركات تستخدم GraphRAG بلا مصدر" --output json

# Demo proof object
python -m mcd.cli kernel-proof-demo --text "النار حارة" --output json
```

---

## Jami/Mani Metrics | مقاييس الجامع/المانع

- **Jami (جامع)**: Coverage score — fraction of required cases covered
- **Mani (مانع)**: Exclusion score — fraction of forbidden cases blocked

Target: both ≥ 0.9 for production readiness.

---

## GPT Residual Contract | عقد البقايا المعرفية لـ GPT

`GPTResidualFoldingContract` enforces the hard invariant: **GPT output is never evidence**. It can only:
- Flag residuals for review
- Suggest tests or invariants
- Pattern-mine for training data

It **cannot** produce `Certificate` proof status or raise `factual_certainty`.
