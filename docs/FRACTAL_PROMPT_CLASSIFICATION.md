# Fractal Prompt Classification Layer (FPCL)

## 1. لماذا البرومبت عقدة معرفية مركبة؟

البرومبت ليس مجرد سؤال لغوي. كل برومبت هو عقدة تحمل:

- **مجالًا معرفيًا** (كون / إنسان / حياة)
- **نوع مفاهيمه** (شيء / خاصية / علاقة / قيمة / نظام / أداة / غاية)
- **صنف المعرفة** (علم / ثقافة / حضارة / مدنية / لغة / منهج)
- **نوع الحكم المطلوب** (معرفي / تقني / قيمي / شرعي / عملي)
- **نوع الدليل اللازم** (حسي / تجريبي / لغوي / نصي / تاريخي / شرعي / تقني / سياقي)
- **سياسة اليقين** (يقين / معرفة راجحة / فرضية / تعليق)

إذا أُرسل البرومبت مباشرة إلى محرك الاستدلال دون تصنيف مسبق، قد يُجيب النظام على سؤال شرعي كأنه علمي، أو على سؤال لغوي كأنه تقني.

FPCL تحل هذا بتصنيف طبيعة البرومبت **قبل** الاستدلال.

---

## 2. ما هي Root Domain؟

```
RootDomain.UNIVERSE  — كون
RootDomain.HUMAN     — إنسان
RootDomain.LIFE      — حياة
```

| Domain   | المعنى |
|----------|--------|
| universe | الموجودات المادية، الطبيعة، القوانين، الأشياء وخواصها، السبب والمسبب الفيزيائي |
| human    | العقل، الإدراك، اللغة، الحاجات، الغرائز، السلوك، التعلم، الشخصية |
| life     | العلاقات، المجتمع، النظام، التربية، الاقتصاد، الثقافة، الحضارة، المشاكل العملية |

مثال: "النار تحرق" → universe / "الكذب ضار" → human + life

---

## 3. ما هي Concept Type؟

```
ConceptType.THING     — شيء
ConceptType.PROPERTY  — خاصية
ConceptType.RELATION  — علاقة
ConceptType.VALUE     — قيمة
ConceptType.SYSTEM    — نظام
ConceptType.TOOL      — أداة
ConceptType.PURPOSE   — غاية
```

| Type     | أمثلة |
|----------|-------|
| thing    | نار، ماء، إنسان، لغة، نموذج |
| property | حار، ضار، نافع، عاقل |
| relation | يسبب، يدل، يتضمن، يقيد |
| value    | خير، شر، عدل، حسن، قبح |
| system   | نظام تعليمي، نظام معرفي |
| tool     | API، ديكودر، GPT، قاعدة بيانات |
| purpose  | لماذا، لأي هدف، ما المقصد |

---

## 4. الفرق بين Knowledge Category و Judgment Type

### Knowledge Category — صنف المعرفة

يصف **طبيعة الموضوع** الذي يتناوله البرومبت:

```
science      — ما يحتاج ملاحظة أو تجربة أو قياسًا
culture      — الأفكار والمفاهيم وجهة النظر والقيم
civilization — منظومة المفاهيم عن الحياة
technology   — الأدوات والتقنيات والصناعة والبرمجة
language     — الدال والمدلول والنحو والصرف والدلالة
method       — طريقة التفكير، الاستدلال، التصنيف، القياس، اليقين
```

### Judgment Type — نوع الحكم

يصف **ما يطلبه البرومبت** من المستدِل:

```
epistemic  — ما هو؟ هل هو صحيح؟ ما الدليل؟
technical  — كيف نبني؟ كيف نبرمج؟
value      — هل هو نافع؟ ضار؟ حسن؟ قبيح؟
shari      — واجب، حرام، مندوب، مكروه، مباح
practical  — ما الخطوات؟ ما الخطة؟
```

**ملاحظة حاكمة:** `ضار ≠ حرام` و `نافع ≠ واجب`. لا يُخلط بين الحكم القيمي والحكم الشرعي.

---

## 5. كيف تحدد Evidence Need؟

FPCL تحدد نوع الدليل اللازم بناءً على:

1. **صنف المعرفة** → مثلاً: science → sensory + experimental
2. **نوع الحكم** → مثلاً: shari → shari + textual
3. **تلميحات المفاهيم** → من قاموس الكلمات

| السياق | الدليل المطلوب |
|--------|--------------|
| نار تحرق | sensory + experimental |
| ما معنى علم؟ | linguistic + contextual |
| هل الكذب حرام؟ | shari + textual |
| كيف نبني API؟ | technical + textual |

---

## 6. كيف تحدد Certainty Policy؟

القواعد بالأولوية:

1. **حكم شرعي بلا دليل شرعي** → `suspend`
2. **لا سياق كافٍ** → `suspend`
3. **سؤال تقني أو عملي** → `strong_knowledge`
4. **علم + دليل حسي/تجريبي** → `strong_knowledge` أو `near_certainty`
5. **حضاري/ثقافي واسع** → `hypothesis`
6. **لغوي (معنى مفهوم غامض)** → `suspend`
7. **معرفي/قيمي مع سياق** → `strong_knowledge`

---

## 7. كيف يعمل التركيب الفركتالي؟

```
V(prompt) = normalize(Σ w_i * V(concept_i) + intent_bias)
```

- كل مفهوم صغير يُصنَّف مستقلًا.
- المتجهات تُجمع بأوزان متساوية.
- `intent_bias` يرفع التصنيفات الملائمة للهدف.
- النتيجة تحافظ على **جميع التصنيفات الثانوية** (لا winner-takes-all).

هذا يمنع النظام من اختزال برومبت مركب في بُعد واحد.

---

## 8. كيف يرتبط FPCL مع MCD و NERL؟

```
User Prompt
↓
Fractal Prompt Classification Layer (FPCL)
↓
PromptFrame (root_domain, concept_types, judgment_types, evidence_needs, certainty_policy)
↓
Router → primary_engine + sub_engines
↓
MCD (Minimal Cognitive Decoder)
↓
NERL (Nabhani Epistemic Reasoning Layer)
↓
Evidence Gate
↓
Certainty Score
↓
Final Answer
```

FPCL لا تغيّر منطق MCD أو NERL، بل تضيف طبقة تصنيف **قبلية** توجّه المسار.

---

## 9. أمثلة

### 9.1 النار تحرق

```json
{
  "raw_text": "النار تحرق",
  "root_domain": {"universe": 0.80},
  "knowledge_categories": {"science": 0.35},
  "judgment_types": {"epistemic": 0.35},
  "evidence_needs": {"sensory": 0.43, "experimental": 0.35},
  "certainty_policy": "strong_knowledge",
  "routing_engine": "nabhani_decoder"
}
```

### 9.2 ما معنى علم؟

```json
{
  "raw_text": "ما معنى علم؟",
  "knowledge_categories": {"language": 0.57},
  "judgment_types": {"epistemic": 0.10},
  "evidence_needs": {"linguistic": 0.49, "contextual": 0.40},
  "certainty_policy": "suspend",
  "warnings": ["ambiguous prompt or insufficient context — judgment suspended"]
}
```

### 9.3 هل الكذب ضار؟

```json
{
  "raw_text": "هل الكذب ضار؟",
  "root_domain": {"human": 0.40, "life": 0.30},
  "judgment_types": {"value": 0.35, "epistemic": 0.35, "shari": 0.10},
  "certainty_policy": "strong_knowledge"
}
```

**ملاحظة:** shari=0.10 لأن "ضار" ليست مصطلحًا شرعيًا.

### 9.4 هل الكذب حرام؟

```json
{
  "raw_text": "هل الكذب حرام؟",
  "judgment_types": {"shari": 0.90},
  "evidence_needs": {"shari": 0.90, "textual": 0.81},
  "certainty_policy": "suspend",
  "warnings": ["shari judgment requires shari evidence"]
}
```

### 9.5 كيف نبني API للديكودر؟

```json
{
  "raw_text": "كيف نبني API للديكودر؟",
  "knowledge_categories": {"technology": 0.47},
  "judgment_types": {"technical": 1.0, "practical": 0.35},
  "evidence_needs": {"technical": 0.85},
  "certainty_policy": "strong_knowledge",
  "routing_engine": "mcd"
}
```

### 9.6 نظام تعليمي عربي بالذكاء الاصطناعي

```json
{
  "raw_text": "كيف نبني نظامًا تعليميًا عربيًا يستخدم الذكاء الاصطناعي لتربية العقل؟",
  "root_domain": {"human": ..., "life": ...},
  "concept_types": {"system": ..., "tool": ..., "purpose": ...},
  "knowledge_categories": {"technology": ..., "culture": ..., "civilization": ...},
  "judgment_types": {"technical": ..., "practical": ...},
  "certainty_policy": "hypothesis"
}
```

يظهر أكثر من domain وأكثر من concept_type — التصنيف غير أحادي.

---

## 10. استخدام CLI

```bash
# تصنيف برومبت (JSON افتراضيًا)
python -m mcd.cli classify "النار تحرق"

# تصنيف بمخرج نصي
python -m mcd.cli classify "هل الكذب حرام؟" --output text

# تصنيف مع معلومات تفصيلية للتشخيص
python -m mcd.cli classify "كيف نبني API؟" --output json --debug
```

---

## 11. TODO للمرحلة التالية

```
1. دمج FPCL مع API (FastAPI endpoint: POST /classify).
2. إضافة evaluation dataset للتصنيف.
3. معايرة weights رياضيًا.
4. ربط classification output مع NabhaniDecoder بشكل أعمق.
5. إضافة Arabic GraphRAG routing.
6. إضافة واجهة FastAPI:
   POST /classify
   POST /nabhani/decode_with_classification
```
