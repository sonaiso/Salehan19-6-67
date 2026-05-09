# Nabhani Epistemic Reasoning Layer (NERL)

## لماذا هذه الطبقة؟

MCD (Minimal Cognitive Decoder) يُنتج تحليلًا لغويًا ومعرفيًا للنصوص العربية: تطبيع، تحليل صرفي، استخلاص علاقات، تسجيل ادعاءات، وتقييم أولي لليقين.

لكن MCD يبقى **محللًا لغويًا**. لا يملك آلية للتفريق بين:
- **الحكم المعرفي** (هل النار تحرق؟ هل الكذب ضار؟)
- **الحكم الشرعي** (هل الكذب حرام؟ هل الصلاة واجبة؟)

ولا يملك آلية للتحقق من أن المعنى مؤسَّس على **واقع مدرك**، أو أن الدليل حقيقي وليس مجرد استعارة لسانية أو تشابه سطحي.

**NERL** يعالج هذه الفجوة بتحويل **منهج تقي الدين النبهاني في العقل والطريقة العقلية** إلى محركات ذكاء اصطناعي قابلة للتنفيذ.

---

## الفرق بين MCD و NERL

| الجانب | MCD | NERL |
|--------|-----|------|
| المدخل | نص عربي | مخرج MCD + السياق |
| الوظيفة | تحليل لغوي ومعرفي | استدلال معرفي منضبط |
| المفهوم | معنى اللفظ | معنى له واقع مدرك |
| الدليل | أي إشارة لغوية | دليل مؤسَّس أو معلَّق |
| اليقين | درجة حسابية | درجة + سياسة + مقياس |
| الحكم الشرعي | لا يُفرِّق | يعزله ويشترط دليلًا شرعيًا |
| المخرج | DecoderOutput | JSON معرفي منضبط |

---

## كيف تحوّل منهج النبهاني إلى محركات؟

### المبدأ الحاكم

```
واقع + حس/مصدر + معلومات سابقة + ربط
+ دال ومدلول + مفهوم + دليل + مطابقة + درجة يقين
= معرفة معرفية منضبطة
```

### المحركات المُنفَّذة

| المحرك | الملف | الوظيفة |
|--------|-------|---------|
| EpistemicAxiom | `epistemic_axioms.py` | 13 أصلًا معرفيًا من منهج النبهاني |
| RationalMethodJudge | `rational_method_judge.py` | يحاكم الادعاء بالطريقة العقلية |
| DomainJudge | `domain_judge.py` | يفصل المعرفي عن الشرعي |
| DalMadlulMapper | `dal_madlul_mapper.py` | دال → مدلول → مفهوم |
| ConceptGrounder | `concept_grounder.py` | يشترط واقعًا لإنتاج مفهوم |
| CorrespondenceChecker | `correspondence_checker.py` | يفحص مطابقة الفكر للواقع |
| FakeEvidenceDetector | `fake_evidence_detector.py` | يكشف الأدلة المزيفة |
| ConflictResolver | `conflict_resolver.py` | يحل تعارض الأدلة |
| CognitiveMeasureBuilder | `cognitive_measure.py` | يرفع اليقين ≥ 0.85 إلى مقياس |
| NabhaniDecoder | `nabhani_decoder.py` | خط الأنابيب الكامل |

---

## المفاهيم الأساسية

### الواقع (Reality)
الشيء أو الحدث أو الحالة الموجودة خارج الذهن. لا معرفة بلا واقع (AX-01).

### المعلومات السابقة (Prior Information)
المخزون المعرفي التراكمي الذي يُمكِّن الذهن من ربط الواقع الجديد بمعنى. ليست رأيًا سابقًا (AX-03, AX-04).

### الربط (Linking)
عملية وصل الواقع المُدرَك بالمعلومات السابقة لإنتاج فكر. بلا ربط لا فكر (AX-05).

### المفهوم (Concept)
ليس مجرد معنى اللفظ، بل معنى **أُدرك له واقع**. "النار" ليست مفهومًا بمجرد النطق بها، بل بإدراك الشيء المُشتعل المُحسوس (AX-06).

### الدليل (Evidence)
الأساس الذي يسند الادعاء ويتجاوز مجرد التصريح. لا معرفة معتبرة بلا دليل (AX-08).

### اليقين (Certainty)
درجة على مقياس من 0 إلى 1. ليس كل معرفة يقينًا (AX-09):
- `weak_or_unverified`: 0.00 – 0.40
- `hypothesis`: 0.40 – 0.60
- `probable_knowledge`: 0.60 – 0.75
- `strong_knowledge`: 0.75 – 0.90
- `near_certainty`: 0.90 – 1.00

---

## لماذا LLM ليس الحاكم النهائي؟

الـ LLM **مقترِح** لا **حاكم**. يُقدِّم مرشحات للمعنى والعلاقات، لكنه:
- قد يُنتج معاني لا واقع لها.
- قد يُظهر ثقةً بلا دليل.
- لا يُفرِّق بالضرورة بين الحكم المعرفي والحكم الشرعي.

NERL يستخدم مخرجات LLM/MCD كـ**مدخل أولي** ثم يُخضعها لمحاكمة معرفية صارمة.

---

## كيف يعمل النظام قبل ورود الشرع؟ (AX-13)

العقل يملك حكمًا معرفيًا عقليًا قبل ورود الشرع:
- يُدرك أن النار تحرق.
- يُدرك أن الكذب يُفسد الثقة ويُضر.
- لكنه **لا يُصدر** حكمًا بالوجوب أو التحريم بلا دليل شرعي.

هذا مُنفَّذ في `DomainJudge`:
```python
judge.classify_text("الكذب ضار")   # → epistemic, proceed_epistemic
judge.classify_text("الكذب حرام")  # → normative_shari, no_shari_ruling_available
```

---

## كيف يفرق بين الحكم المعرفي والحكم الشرعي؟

| النوع | أمثلة | مصدر الحكم | حالة بلا دليل |
|-------|--------|------------|---------------|
| معرفي | ضار، نافع، صحيح، خاطئ، موجود | العقل والحس | `proceed_epistemic` |
| شرعي | حرام، واجب، مباح، مكروه | الدليل الشرعي | `no_shari_ruling_available` |

الكلمات المُكتشَفة تلقائيًا:
- **معرفي**: ضار، ضرر، نافع، يفيد، مفيد
- **شرعي**: حرام، واجب، فريضة، يجب، فرض، محرم

---

## أمثلة تشغيل

### من CLI:
```bash
# تحليل معرفي
python -m mcd.cli nabhani "النار تحرق"

# تمييز الحكم
python -m mcd.cli nabhani "الكذب ضار"
python -m mcd.cli nabhani "الكذب حرام"

# مخرج JSON
python -m mcd.cli nabhani "العلم نافع" --output json
```

### من Python:
```python
from mcd.nabhani.nabhani_decoder import NabhaniDecoder

decoder = NabhaniDecoder()

# النار تحرق
result = decoder.decode("النار تحرق")
print(result["epistemic_status"])   # "verified" or "probable"
print(result["domain"]["judgment_type"])  # "epistemic"

# الكذب حرام
result = decoder.decode("الكذب حرام")
print(result["domain"]["status"])   # "no_shari_ruling_available"
print(result["epistemic_status"])   # "suspended"
```

### مثال المخرج (النار تحرق):
```json
{
  "input": "النار تحرق",
  "domain": {
    "judgment_type": "epistemic",
    "status": "proceed_epistemic",
    "can_reason_without_revelation": true
  },
  "rational_judgment": {
    "accepted": true,
    "status": "accepted"
  },
  "correspondence": {
    "match_score": 0.75,
    "match_type": "prior_knowledge_match"
  },
  "certainty": {
    "score": 0.85,
    "level": "strong_knowledge"
  },
  "epistemic_status": "probable"
}
```

---

## ما بقي للمرحلة التالية

- دعم `revelation_evidence` من مصادر نصية خارجية.
- تكامل أعمق مع قاعدة معرفة النبهاني (علاقات الفقه، الأصول).
- محرك `RuleComposer` يبني قواعد من `CognitiveMeasure` المتراكمة.
- دعم متعدد اللغات (التحليل بالعربية والاستدلال بأي لغة).
- واجهة REST API.
