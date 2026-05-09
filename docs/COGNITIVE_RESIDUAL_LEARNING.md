# Cognitive Residual Learning — Phase 7

**Formula:**

```
CognitiveResidual = GPTProposal − MathematicalContract
```

**Governing Principle:**

> GPT suggests. Mathematical Contract judges. Cognitive Residual teaches.

---

## 1. لماذا GPT ليس حاكمًا؟

GPT (أو أي نموذج لغوي خارجي) هو نظام احتمالي يستخرج الأنماط من بيانات التدريب. إخراجه:

- **ليس دليلاً** — لأن الدليل يتطلب مصدرًا خارجيًا موثوقًا، ومنهجية تحقق، وقابلية للفحص.
- **لا يرفع اليقين** — لأن اليقين يُبنى على أدلة، لا على إجماع نموذج.
- **لا يستطيع الفصل بين الضار والحرام** — لأن هذا قرار شرعي يحتاج إلى علة، ليس مجرد ارتباط إحصائي.
- **يمكن خداعه بحقن النصوص** — وهذا يجعله خطرًا إذا كان حاكمًا.

لذلك GPT يُستخدم **كمقترح** (Proposer) فقط، لا كحكم (Judge).

---

## 2. ما معنى GPT Proposal؟

`GPTProposal` هو مخرج LLM خارجي تم تحويله إلى كيان بيانات رسمي:

```python
GPTProposal:
    proposal_id: str          # معرف فريد
    input_text: str           # السؤال أو المدخل الأصلي
    gpt_output: str           # مخرج GPT (proposal فقط — ليس حقيقة)
    proposal_type: ProposalType  # answer / explanation / dataset_example / ...
    claimed_evidence: list[str]  # ما يدعي GPT أنه دليل
    claimed_certainty: str | None  # مستوى اليقين المدّعى
    metadata: dict            # معلومات إضافية
```

**قاعدة أساسية:** `gpt_output` ≠ دليل. `claimed_evidence` لا يُقبل إلا بعد فحص المحرك.

---

## 3. ما معنى Mathematical Contract؟

`MathematicalContract` هو مجموعة قواعد صارمة تُطبَّق على أي مقترح قبل قبوله:

| القاعدة | الوصف |
|---------|-------|
| [1] graph not empty | الرسم البياني لا يكون فارغًا |
| [2/3] vectors valid | كل عقدة تمتلك vectors صحيحة |
| [4] edge endpoints | كل حافة لها بداية ونهاية في الرسم |
| [5] cause has effect | كل سبب له أثر |
| [7] near_certainty + evidence | اليقين يحتاج دليلاً |
| [8] ambiguous → suspend | الغموض يستلزم التعليق |
| [9] harm ≠ haram | الضار لا يستلزم الحرام |
| [10] tool/API ≠ evidence | الأدوات والـAPI لا تكون دليلاً وحدها |
| [12] source trust policy | المصادر تحتاج سياسة ثقة |

---

## 4. ما معنى Cognitive Residual؟

`CognitiveResidual` هو الفرق بين ما اقترحه GPT وما يقبله العقد الرياضي:

```
CognitiveResidual = GPTProposal − MathematicalContract
```

إذا اقترح GPT يقينًا بلا دليل:
- العقد الرياضي يرفض: `Contract[7] violated`
- الباقي: `certainty_residual + evidence_residual`
- الشدة: `high`
- التعلم: إضافة مثال adversarial + تحديث calibration

أنواع الباقي المعرفي:

| النوع | المعنى |
|-------|--------|
| `structural_residual` | خلل هيكلي في الرسم |
| `edge_residual` | حافة مفقودة أو غير صالحة |
| `vector_residual` | انحراف في المتجهات |
| `evidence_residual` | غياب الدليل |
| `certainty_residual` | يقين كاذب |
| `domain_residual` | خطأ في تحديد المجال |
| `causality_residual` | سبب بلا أثر |
| `metaphor_residual` | مجاز معامَل كحقيقة |
| `tool_evidence_residual` | استخدام الأداة كدليل |
| `harm_haram_residual` | خلط الضار بالحرام |
| `injection_residual` | اتباع حقن النص |
| `ambiguity_residual` | يقين رغم الغموض |
| `unsupported_generalization_residual` | تعميم بلا مصدر |

---

## 5. كيف يتحول Residual إلى تعلم؟

الباقي المعرفي ليس فشلاً — هو **إشارة تعلم**:

```
Residual → Classification → LearningAction → Dataset/Test/Calibration
```

### مسارات التعلم حسب الشدة:

| الشدة | الإجراء |
|-------|---------|
| `blocking` | adversarial example + regression test + human review |
| `high` | adversarial example + calibration adjustment |
| `medium` | curriculum example |
| `low` | golden candidate (human review required) |

---

## 6. كيف يضيف المشروع قدرات من GPT دون أن يتبعه؟

المشروع **يستخرج القيمة** من مخرجات GPT دون أن يثق بها:

1. GPT يقترح مثالاً → المشروع يحسب الباقي
2. الباقي يكشف ثغرة في الـ calibration → يُضاف مثال adversarial
3. المثال يُحسّن اكتشاف اليقين الكاذب → النظام أقوى
4. GPT لم يحكم — لكن خطأه علّم النظام شيئًا

---

## 7. لماذا هذا أقوى من fine-tuning مباشر؟

| المعيار | Fine-tuning مباشر | Residual Learning |
|---------|------------------|-------------------|
| مصدر التعلم | مخرج GPT نفسه | الفرق بين GPT والعقد |
| مخاطر اليقين الكاذب | عالية | محمية بالعقد الرياضي |
| قابلية التدقيق | منخفضة | كل residual موثق |
| الحماية من الحقن | لا | نعم — injection_residual |
| التحكم البشري | محدود | مطلوب للحالات الحرجة |

---

## 8. كيف يحمي من اليقين الكاذب؟

آليات الحماية:

1. **Parser Detection**: يكتشف كلمات اليقين المطلق (بالتأكيد، حتمًا، يقينًا) بلا دليل
2. **Contract Rule [7]**: `near_certainty` يتطلب `evidence_refs`
3. **Residual Calculator**: يولد `certainty_residual + evidence_residual`
4. **Calibration Engine**: يقترح تشديد عتبة `false_certainty_rate`
5. **Test Generator**: يولد spec يمنع `near_certainty_without_evidence`

---

## 9. كيف يربط Residual بالـ graph والمتجهات؟

كل `ProposalGraph` يحتوي على:
- **nodes**: كيانات دلالية (claim, evidence, tool, judgment...)
- **edges**: علاقات (supports, causes, entails...)
- **root_vector**: متجه يقيس قيم مثل `evidence_strength`, `certainty_claim`
- **evidence_status**: sufficient / insufficient / missing

الباقي المعرفي يقيس:
- `vector_deviations`: انحراف المتجه عن القيم المتوقعة
- `missing_nodes`: عقد مفقودة (مثل: evidence_refs فارغة)
- `invalid_edges`: حواف تنتهك القواعد (harm→haram entails)

---

## 10. كيف يدخل في curriculum/calibration/industrial tests؟

```
GPTProposal
    ↓ ProposalParser
ProposalGraph
    ↓ MathematicalContract
ContractResult (violations + warnings)
    ↓ ResidualCalculator
CognitiveResidual
    ↓ ResidualClassifier
ResidualClassification (priority, target_datasets)
    ↓ LearningRouter
LearningActions:
    ├── add_curriculum_example → data/curriculum/
    ├── add_adversarial_example → data/residual_learning/generated_adversarial.jsonl
    ├── add_regression_test → tests/
    ├── propose_invariant → invariant candidates
    ├── adjust_calibration → calibration recommendations
    └── require_human_review → human review queue
```

---

## CLI Commands

```bash
# تحليل المقترحات وحساب الباقي المعرفي
python -m mcd.cli residual-analyze \
    --input data/residual_learning/mock_gpt_proposals_ar.jsonl \
    --output json

# تقرير ملخص
python -m mcd.cli residual-report --output markdown

# بناء مجموعة adversarial
python -m mcd.cli residual-build-dataset \
    --target adversarial \
    --output data/residual_learning/generated_adversarial.jsonl

# توصيات calibration
python -m mcd.cli residual-calibrate --output markdown

# توليد test specs
python -m mcd.cli residual-test-specs \
    --output data/residual_learning/generated_test_specs.jsonl
```

---

## Quality Rules

1. ✅ GPT output is **never** evidence
2. ✅ GPT output **cannot** increase certainty
3. ✅ Every proposal must pass MathematicalContract
4. ✅ Residual is a learning signal, not final truth
5. ✅ Blocking residuals create adversarial candidate + regression test
6. ✅ Golden examples require human review
7. ✅ No real GPT API calls in tests
8. ✅ No network calls in CI
9. ✅ No GraphRAG
10. ✅ No automatic writes to core datasets without explicit output path
