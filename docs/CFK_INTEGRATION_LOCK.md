# CFK Integration Lock — Phase 8.1

## الهدف

وثيقة **CFK Integration Lock** تشرح لماذا الـ Cognitive Fractal Kernel (CFK) ليس مجرد طبقة مضافة، بل هو **الحاكم الرياضي المركزي** لكل الطبقات.

---

## 1. لماذا CFK ليس طبقة عادية؟

الطبقات العادية في النظام (مثل Mabni، Murab، Morphosemantics) تحلل نصًا وتنتج معلومات لغوية أو تركيبية.
CFK يختلف عنها جذريًا:

| الطبقة العادية | CFK |
|----------------|-----|
| تحلل النص | يحكم على الحالة المعرفية |
| تنتج مخرجات لغوية | يصدر حكمًا نهائيًا |
| مستقلة | يستقبل projections من كل الطبقات |
| قد تتعارض مع بعضها | يحسم التعارض ويفرض قواعد الحفظ |

```
GPT/statistical → projection فقط
Arabic/mabni/murab → projection فقط
Epistemic/evidence → projection
CFK → judgment
ProofObject → final status
```

لا يسمح لأي طبقة فرعية بإصدار Certificate وحدها. هذا الحق محفوظ لـ ProofObjectBuilder فقط،
وهو نفسه لا يصدر Certificate إلا بعد استيفاء ثلاثة شروط (انظر القسم 6).

---

## 2. لماذا كل الطبقات projections فقط؟

```
F(U) = ⟨N, V, R, O, E, C, P, T, Z⟩
```

كل طبقة "تسقط" الوحدة المعرفية في نظام إحداثياتها:

- **S(x)** — الإسقاط الإحصائي: "ما أكثر الاحتمالات في هذا السياق؟"
- **A(x)** — الإسقاط العربي الدلالي: "ما القوة اللغوية والعلاقة التركيبية؟"
- **E(x)** — الإسقاط المعرفي: "ما درجة يقينية بناءً على الأدلة؟"

ثم **K** (الـ Kernel) يجمع الإسقاطات الثلاثة في فضاء واحد قابل للمقارنة.

الطبقات الفرعية لا تعطي يقينًا نهائيًا لأنها:
1. تعمل في أنظمة إحداثيات مختلفة (إحصائية / لغوية / برهانية).
2. لا تملك المعلومات الكاملة لإصدار حكم.
3. قد تتعارض مع بعضها — CFK هو من يحسم.

---

## 3. لماذا statistical confidence لا يساوي epistemic certainty؟

```
statistical_confidence = P(x | corpus) = احتمال ظهور x في المدونة
epistemic_certainty    = P(x | evidence) = يقين مستند إلى دليل حقيقي
```

النموذج اللغوي (GPT) يعطي احتمالًا إحصائيًا، لا يقينًا معرفيًا.

**المعادلة الصحيحة:**
```
C_epistemic = G(C_statistical, E, R, T)
```

- إذا `evidence_state = missing`: `C_epistemic ≤ 0.40`
- إذا `evidence_state = partial`: `C_epistemic ≤ 0.65`
- إذا `evidence_state = present`: يُحسب من كل المدخلات

**القاعدة:**
```
high statistical_confidence + no evidence ≠ certificate
```

---

## 4. لماذا Arabic force لا يساوي evidence؟

القوة اللغوية (linguistic force) هي خاصية بنيوية في الجملة العربية:
- `إنّ` = توكيد
- `لا` = نفي
- `كل` = تعميم
- `إذا` = شرط

لكن التوكيد اللغوي ليس دليلًا على صحة المحتوى:

```
إن هذا الدواء يشفي كل مرض         ← توكيد لغوي
لكن: لا يوجد دليل تجريبي           ← يبقى فرضية
→ A(x) لا يرفع epistemic_certainty
→ A(x) لا يُصدر Certificate
```

**عقد الطبقة العربية:**
```
can_create_evidence = False
can_raise_epistemic_certainty = False
can_set_linguistic_force = True  ← هذا فقط مسموح
```

أيضًا: إذا فشل murab أو mabni (fallback mode)، يجب:
1. تسجيل `murab_fallback=True` / `mabni_fallback=True` في metadata.
2. تحديد نبذة في `transform_notes`.
3. حصر `comparable_score ≤ 0.55`.

---

## 5. لماذا syntactic certainty لا يساوي factual certainty؟

I'rab (الإعراب) يحدد الدور التركيبي للكلمة في الجملة:
- `الطالبُ` (مرفوع) = فاعل
- `الطالبَ` (منصوب) = مفعول به

هذا يقين **تركيبي** فقط، ليس يقينًا **واقعيًا**:

```
جاء الطالبُ.    ← يقين تركيبي: الطالب هو الفاعل
لكن: هل جاء فعلًا؟  ← يحتاج دليلًا
```

**عقد طبقة Murab:**
```
can_raise_syntactic_certainty = True   ← مسموح
can_raise_factual_certainty = False    ← ممنوع
can_raise_epistemic_certainty = False  ← ممنوع
```

والتحقق الصناعي في CrossLayerConservationChecker يضمن:
```
if murab_syntactic == "certain_syntactic" and evidence_state == "missing":
    epistemic_certainty must stay ≤ 0.40
```

---

## 6. لماذا Certificate يحتاج ProofObject + ReverseTrace؟

شهادة اليقين (Certificate) هي أعلى درجة في نظام الحكم. لتصدر، يجب استيفاء **ثلاثة شروط معًا**:

### الشرط الأول: evidence_refs غير فارغة
```python
if not evidence_refs:
    judgment = "hypothesis"  # لا يمكن certificate
```

### الشرط الثاني: لا يوجد blocking conservation violation
```python
if any(v.severity == "blocking" for v in conservation.violations):
    judgment = "zero"  # تدمير بنيوي
```

### الشرط الثالث: ReverseTrace.complete = True
```python
if not reverse_trace.complete:
    judgment = "hypothesis"  # لا يمكن certificate بدون trace كامل
```

**ReverseTrace** يربط الحكم بكل مصادره:
```
ReverseTrace:
  ├── statistical_projection_id (KP-S-...)
  ├── arabic_projection_id      (KP-A-...)
  ├── epistemic_projection_id   (KP-E-...)
  ├── evidence_refs             [e1, e2, ...]
  ├── conservation_refs         [unit_ids]
  └── complete: bool
```

---

## 7. كيف يمنع CFK تضارب Mabni/Mu'rab/Morphosemantics؟

الطبقات قد تتعارض:
- Mabni يقول: هذه الجملة توكيد (إن).
- Murab يقول: الفاعل مرفوع (يقين تركيبي).
- Morphosemantics يقول: الجذر يدل على المعرفة.

بدون CFK، هذه المخرجات المتضاربة قد تؤدي إلى:
- رفع يقين معرفي بدون دليل.
- إصدار Certificate من طبقة فرعية.
- تعارض في الحكم النهائي.

**CFK يحل هذا بـ:**

1. **CFKIntegrationContract** — يحدد ما يمكن لكل طبقة فعله.
2. **ConservationLawChecker** — يفحص قوانين الحفظ داخل كل وحدة.
3. **CrossLayerConservationChecker** — يفحص قوانين الحفظ **عبر** الطبقات.
4. **ProofObjectBuilder** — يصدر الحكم النهائي بعد كل الفحوصات.

النتيجة: لا طبقة تستطيع تجاوز الـ Kernel، ولا يقين بدون دليل.

---

## قواعد الـ Pipeline الكامل

```
GPTProposal
→ S(x): StatisticalTransform     [projection: احتمال فقط]
→ A(x): ArabicSemanticTransform  [projection: قوة لغوية فقط]
→ E(x): EpistemicTransform       [projection: يقين بناءً على أدلة]
→ K:    FractalKernel            [judgment: يوحد الثلاثة]
→ ConservationLawChecker         [intra-unit: 5 قوانين]
→ CrossLayerConservationChecker  [cross-layer: 8 فحوصات]
→ ReverseTraceBuilder            [trace: ربط الحكم بمصادره]
→ ProofObjectBuilder             [certificate gate: 3 شروط]
→ ProofObject: Certificate | Hypothesis | Suspend | Zero
```

---

## CLI Commands (Phase 8.1)

```bash
# التحقق من صحة عقود التكامل
python -m mcd.cli cfk-validate --text "النار حارة" --output json

# تقرير تكامل كامل
python -m mcd.cli cfk-integration-report --text "النار حارة" --output markdown

# فحص Conservation عبر الطبقات
python -m mcd.cli cfk-conservation --text "كل الشركات تستخدم GraphRAG" --output json

# بناء Reverse Trace
python -m mcd.cli cfk-reverse-trace --text "النار حارة" --evidence "empirical_1,exp_2" --output markdown
```

---

## معايير القبول (Acceptance Criteria)

| # | المعيار | الملاحظة |
|---|---------|----------|
| 1 | `CFKIntegrationContract` موجود | `src/mcd/cfk/cfk_integration_contract.py` |
| 2 | لا silent fallback في `ArabicSemanticTransform` | يُسجل في metadata، يحصر Score ≤ 0.55 |
| 3 | `CrossLayerConservationChecker` موجود | `src/mcd/cfk/cross_layer_conservation.py` |
| 4 | `ReverseTrace` مربوط بـ `ProofObject` | `src/mcd/cfk/reverse_trace.py` |
| 5 | Certificate يشترط evidence + reverse_trace + conservation | `proof_object.py` |
| 6 | statistical confidence عالية بدون evidence → لا certificate | قاعدة مفروضة |
| 7 | توكيد بدون evidence → لا certificate | قاعدة مفروضة |
| 8 | syntactic certainty بدون evidence → لا certificate | قاعدة مفروضة |
| 9 | trace completeness بدون evidence → لا certificate | قاعدة مفروضة |
| 10 | CLI commands تعمل | 4 أوامر جديدة |
| 11 | كل الاختبارات تنجح | 127 + اختبارات Phase 8.1 |
| 12 | لا GPT calls | ✓ |
| 13 | لا network calls | ✓ |
| 14 | لا GraphRAG | ✓ |
| 15 | لا API expansion | ✓ |
