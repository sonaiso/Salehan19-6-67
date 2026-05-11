# التعلم المعرفي القابل للطي — الوثيقة الشاملة

## المرحلة 7.2: Foldable Cognitive Residual Learning

---

## 1. المقدمة والهدف

تهدف هذه المرحلة إلى بناء منظومة تعلم معرفي قادرة على تحديد الفجوات المعرفية في مخرجات النماذج اللغوية (GPT) ومعالجتها عبر سلسلة رياضية محكمة:

```
GPT Proposal − Mathematical Contract = Cognitive Residual
→ Fold Signature → Pattern Memory → Recall → Learning Action
```

**القيود الأساسية:**
- لا اتصال بشبكة خارجية
- لا استدعاء حقيقي لـ GPT API
- لا GraphRAG
- مخرجات GPT **ليست أدلة** في أي حال

---

## 2. الصيغة الرياضية

```
R = P − C
```

حيث:
- `P` = مقترح GPT (GPT Proposal)
- `C` = العقد الرياضي (Mathematical Contract)
- `R` = البقايا المعرفية (Cognitive Residual)
- `F(R)` = توقيع الطي (Fold Signature)
- `M[F]` = ذاكرة الأنماط (Pattern Memory)
- `Recall(M, context)` = استدعاء النمط
- `Action(R)` = إجراء التعلم

---

## 3. مكونات الحزمة

### `src/mcd/foldable_learning/`

| الملف | الغرض |
|-------|--------|
| `proposal_schema.py` | إعادة تصدير GPTProposal, ProposalType |
| `proposal_parser.py` | المحلل الموسّع — يكشف GPT كدليل، API كسلطة، مصادر قديمة |
| `residual_schema.py` | ResidualType موسّع مع GPT_AS_EVIDENCE, TRACEABILITY |
| `residual_calculator.py` | حاسب البقايا الموسّع |
| `residual_classifier.py` | مصنّف البقايا حسب الخطورة |
| `fold_schema.py` | FoldSignature dataclass |
| `fold_signature.py` | FoldSignatureRegistry مع 15 عائلة طي |
| `residual_to_fold.py` | محوّل البقايا إلى توقيعات طي |
| `pattern_memory.py` | ذاكرة الأنماط في الذاكرة |
| `recall_engine.py` | محرك الاستدعاء |
| `unfold_plan.py` | خطة إلغاء الطي |
| `learning_action_router.py` | موجّه إجراءات التعلم |
| `mathematical_pattern_miner.py` | مُعدِّن الأنماط الرياضية |
| `fold_unfold_consistency.py` | مدقق الاتساق |
| `mock_gpt_outputs.py` | مولّد المقترحات الاختبارية |
| `foldable_report.py` | مولّد التقارير والمقاييس |
| `serializers.py` | أدوات التسلسل |

---

## 4. أنواع البقايا المعرفية

| النوع | الشدة | الوصف |
|-------|-------|-------|
| `gpt_as_evidence_residual` | blocking | استخدام GPT كدليل — محظور |
| `harm_haram_residual` | blocking | الربط الخاطئ بين الضرر والحرام |
| `injection_residual` | blocking | حقن التوجيهات |
| `tool_evidence_residual` | high | API كسلطة مرجعية |
| `traceability_residual` | high | مصادر قديمة |
| `evidence_residual` | medium | غياب الدليل |
| `certainty_residual` | medium | يقين بلا مبرر |
| `metaphor_residual` | medium | تحويل المجاز إلى حقيقة |
| `domain_residual` | medium | خطأ تخصصي |
| `unsupported_generalization_residual` | medium | تعميم بلا دليل |
| `ambiguity_residual` | low | غموض غير معالج |
| `analogy_residual` | low | قياس بلا علة |
| `causality_residual` | low | سببية خاطئة |

---

## 5. عائلات توقيعات الطي

يحتوي `FoldSignatureRegistry` على 15 عائلة طي مسجّلة مسبقاً:

1. `FOLD-EVIDENCE-GAP` — فجوة الدليل
2. `FOLD-CERTAINTY-WITHOUT-BASIS` — يقين بلا أساس
3. `FOLD-HARM-HARAM` — خلط الضرر بالحرام
4. `FOLD-GPT-AS-EVIDENCE` — GPT كدليل
5. `FOLD-TOOL-API-AUTHORITY` — API كسلطة
6. `FOLD-METAPHOR-LITERAL` — مجاز حرفي
7. `FOLD-ANALOGY-NO-ILLAH` — قياس بلا علة
8. `FOLD-UNSUPPORTED-GENERALIZATION` — تعميم مدعوم
9. `FOLD-STALE-SOURCE` — مصدر قديم
10. `FOLD-CONFLICT-IGNORED` — تعارض مهمل
11. `FOLD-AMBIGUITY-IGNORED` — غموض مهمل
12. `FOLD-PROMPT-INJECTION` — حقن التوجيهات
13. `FOLD-DOMAIN-ERROR` — خطأ تخصصي
14. `FOLD-CAUSALITY-ERROR` — خطأ سببي
15. `FOLD-TRACEABILITY-GAP` — فجوة التتبع

---

## 6. مسار إجراءات التعلم

### الحالة الخاصة: `gpt_as_evidence_residual`

يستدعي دائماً:
- `reject_proposal` — رفض المقترح
- `add_regression_test` — إضافة اختبار انحدار
- `require_human_review` — مراجعة بشرية إلزامية

### الشدة `blocking`

- `add_regression_test`
- `add_adversarial_example`
- `require_human_review`

### الشدة `high`

- `add_adversarial_example`
- `adjust_calibration`

### الشدة `medium/low`

- `add_curriculum_example`

### اقتراح الثوابت (batch_route)

عند تكرار نوع بقايا ≥ 3 مرات → `propose_invariant`

---

## 7. المقاييس والعتبات

| المقياس | العتبة | النتيجة الحالية |
|---------|--------|----------------|
| fold_consistency_score | ≥ 0.95 | 1.00 ✅ |
| residual_coverage_score | ≥ 0.90 | 1.00 ✅ |
| recall_precision_estimate | ≥ 0.85 | 0.87 ✅ |
| pattern_reuse_rate | ≥ 0.50 | 0.88 ✅ |

---

## 8. أوامر CLI

```bash
# تشغيل خط الأنابيب الكامل
PYTHONPATH=src python -m mcd.cli fold-residuals --output json

# تقرير الذاكرة والمقاييس
PYTHONPATH=src python -m mcd.cli fold-memory-report --output markdown

# استدعاء نمط لنص معين
PYTHONPATH=src python -m mcd.cli fold-recall --text "هذا صحيح" --output json

# فحص اتساق الطي وإلغائه
PYTHONPATH=src python -m mcd.cli fold-consistency --output json

# استخراج الأنماط الرياضية
PYTHONPATH=src python -m mcd.cli pattern-mine --output json
```

---

## 9. ملفات البيانات

| الملف | الوصف |
|-------|-------|
| `mock_gpt_proposals_ar.jsonl` | 100 مقترح عربي عبر 16 فئة |
| `residual_patterns_ar.jsonl` | 20 نمط بقايا مُعدَّن |
| `fold_signatures_ar.jsonl` | 15 توقيع طي |
| `pattern_memory_seed_ar.jsonl` | 15 إدخال ذاكرة أولية |
| `fold_unfold_tests_ar.jsonl` | 20 حالة اختبار |

---

## 10. الاختبارات

تشمل مجموعة الاختبارات 60+ اختباراً جديداً في 9 ملفات:

| الملف | الاختبارات |
|-------|------------|
| `test_foldable_proposal_schema.py` | 6 |
| `test_proposal_parser.py` | 8 |
| `test_foldable_residual_calculator.py` | 9 |
| `test_foldable_residual_classifier.py` | 6 |
| `test_residual_to_fold.py` | 7 |
| `test_pattern_memory.py` | 6 |
| `test_recall_engine.py` | 5 |
| `test_fold_unfold_consistency.py` | 6 |
| `test_mathematical_pattern_miner.py` | 6 |
| `test_learning_action_router.py` | 6 |
| `test_foldable_cli.py` | 5 |

```bash
PYTHONPATH=src python -m pytest tests/ -q
# 1873 passed
```
