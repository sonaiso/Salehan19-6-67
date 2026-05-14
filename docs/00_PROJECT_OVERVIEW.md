# Project Overview

## التعريف المختصر

Bayani / AFJG هو نظام حوكمة معرفية للتحقق من الادعاءات والنصوص العربية ومخرجات النماذج ومخرجات تدقيق الـPRs، ويُصدر فقط الأحكام النهائية التالية:

- ZERO
- HYPOTHESIS
- CERTIFICATE

هذا المستودع ليس نموذجًا لغويًا عامًا، بل منصة تحقق حاكمة تفصل بين التحليل اللغوي والدليل، وبين الدمج البرمجي والشهادة المعرفية.

## الرؤية

الرؤية هي بناء مسار معرفي قابل للتتبع من الواقع حتى الحكم النهائي، بحيث لا يرتفع اليقين دون دليل حاكم، ولا تُصدر شهادة دون بوابات الإثبات والحوكمة والتتبع العكسي.

## المعمارية العليا (القانون الحاكم)

```text
Reality -> Cognitive Distinction -> Linguistic Signification -> Conceptual Geometry -> Direct Meaning -> Licensed Implication -> Claim -> Evidence -> Judgment -> ReverseTrace
```

ويُلزم المشروع كل وحدة معمارية بإظهار:

- pre / current / post
- phi_in / phi_out
- beta
- type / order / composition
- invariants
- forbidden transitions
- residual
- judgment

## الهوية المعمارية

- **AFJG**: الدستور الحاكم للانتقالات المعرفية والأحكام
- **Bayani**: طبقة التحقق المعرفي العربي
- **MCD (`src/mcd`)**: مساحة التنفيذ (CLI/API/Runtime/Tests)
- **Coding Copilot Auditor**: تطبيق صناعي داخلي لتدقيق PRs بحوكمة معرفية

## تحليل تطور المشروع عبر جميع الـPRs (من #1 إلى #99)

السجل الكامل يضم **99 PR** مغلقة، ويمكن تلخيصها إلى موجات تطور واضحة:

1. **التأسيس المواصفاتي والحوكمي (#1–#12)**
   - تأسيس المواصفة والمخططات واختبارات التحقق الأساسية.
2. **محرك المستدل والديكودر المعرفي (#13–#20)**
   - بناء نواة MCD وتصنيف النية والطبقات المعرفية.
3. **التقييم والجاهزية الصناعية المبكرة (#21–#31)**
   - توسعات التقييم، الاختبارات الصناعية، وبداية مسارات API.
4. **التعلم المتبقي والعربية العميقة (#32–#44)**
   - Residual Learning، تتبع Unicode، morphosemantics، mabni/mu'rab، ونواة هندسة كسيرية.
5. **نواة CFK والحوكمة الرياضية (#45–#54)**
   - توحيد الطبقات، الحوكمة الرياضية، وضبط مسار الصعود المعرفي.
6. **حوكمة الهوية وإصلاحات الدمج الحساسة (#55–#61)**
   - إصلاحات تعارضات الدمج، وترسيخ قاعدة: MERGED != CERTIFICATE.
7. **مرحلة Phase 0 وما بعدها (Nabhani + العقود المعرفية) (#62–#88)**
   - مفردات تشغيلية معرفية، عقود الانتقال، اختبار الهجمات المضادة، الجاهزية العلمية/الصناعية.
8. **حزمة التأهيل الخارجي والتصليب والإطلاق المرشح (#89–#92)**
   - حزمة تدقيق خارجية، أمان ونشر، وتقارير release candidate.
9. **حوكمة ولادة الجواب وبيانات التعلم (#93–#99)**
   - Thinking Algebra، حوكمة answer birth، عقود feature adapter، تنبؤ حاكم، ومولد بيانات اصطناعية.

## المنهجية (Method)

المنهج المعتمد في المشروع:

1. **Mind precedes language**: الذهن يسبق اللفظ.
2. **Language reveals mind**: اللغة تكشف البنية الإدراكية ولا تُثبت الحقيقة بذاتها.
3. **Evidence-governed judgment**: الحكم النهائي لا يُرفع إلا بدليل مناسب لنوع الدعوى.
4. **Certificate gating**: لا CERTIFICATE بدون:
   - ProofObject
   - GovernanceGate (passed)
   - ReverseTrace (complete)
5. **Residual preservation**: عدم محو المتبقيات المعرفية (residuals).
6. **Forbidden transition blocking**: منع الانتقالات المحظورة (مثل model_output_as_evidence).

## الرياضيات الحاكمة (Math Governance)

الحوكمة الرياضية تضبط الانتقال عبر المستويات المعرفية من L0 حتى الحكم النهائي، وتفرض:

- تسجيل morphism لكل انتقال معرفي
- حفظ trace/evidence_need/certainty_cap/residual
- قوانين Fold/Unfold/Refold دون رفع يقين صوري
- حساب Jami/Mani وconcept tightness
- منع تحويل إشارات لغوية أو مخرجات أداة إلى دليل أو شهادة مباشرة

## المدخلات (Inputs)

المدخلات التشغيلية الأساسية في المشروع تشمل:

1. **نصوص عربية** (للتحليل والتصنيف والربط)
2. **ادعاءات معرفية** (Claim-centric evaluation)
3. **مخرجات نماذج لغوية** (تُفحص كمواد تحليل لا كدليل)
4. **أدلة وسياقات تحقق** (Evidence artifacts)
5. **بيانات PR/Checks/Traces** لتدقيق البرمجيات حوكميًا
6. **ملفات بيانات تعليمية/تقييمية** (JSON/JSONL) لمسارات dataset/curriculum/residual

## المخرجات (Outputs)

المخرجات الحاكمة الأساسية:

1. **الحكم النهائي العام**: ZERO أو HYPOTHESIS أو CERTIFICATE فقط
2. **reverse trace** كامل لمسار التكوين
3. **residuals** محفوظة وصريحة عند النقص أو التعارض
4. **تقارير جاهزية وتدقيق** (pilot/release/audit/readiness)
5. **مخرجات CLI/API** بهيكل JSON منضبط في المسارات المؤهلة

## النتائج الحالية (Results)

### نتائج تقنية موثقة

- تشغيل `tests/verify_bayani_repository.py`: ناجح.
- تشغيل الاختبارات الشاملة:
  - `PYTHONPATH=src:. python -m pytest -q`
  - **2898 passed, 1 skipped, 2 warnings**

### النتيجة العلمية والصناعية الحالية

- **تقييم نطاق الحزمة (metadata تشغيلية):** المسار العلمي = HYPOTHESIS (أدلة جزئية مع حدود الإغلاق الشكلي).
- **تقييم نطاق الحزمة (metadata تشغيلية):** المسار الصناعي للإنتاج = HYPOTHESIS، مع أهلية نطاق تجريبي محكوم.
- **تنبيه حوكمي:** هذا التقييم ليس طبقة حكم رابعة؛ الحكم النهائي يبقى محصورًا في ZERO/HYPOTHESIS/CERTIFICATE فقط.
- **الحكم النهائي على دعوى "المشروع جاهز للإنتاج الآن":** ZERO.

## واجهات الاستخدام الرئيسية (مختصر)

- CLI عبر `python -m mcd.cli`
- API (pilot profile) عبر `python -m mcd.cli api --host 127.0.0.1 --port 8000`
- مسارات أساسية:
  - `decode`, `classify`, `ground`, `nabhani`
  - `pilot-readiness`, `governance-audit`, `governance-replay`
  - `curriculum-*`, `residual-*`, `readiness-report`

## ما الذي لا يدّعيه المشروع

- ليس بديلًا عن LLM عام.
- لا يعتبر نجاح CI وحده شهادة معرفية.
- لا يعتبر حالة `MERGED` حكمًا نهائيًا.
- لا يرفع أي مسار إلى CERTIFICATE دون شروط الشهادة الكاملة.

## مراجع القراءة التالية

- [Architecture Map](01_ARCHITECTURE_MAP.md)
- [Product Roadmap](02_PRODUCT_ROADMAP.md)
- [Judgment Model](03_JUDGMENT_MODEL.md)
- [Merge Governance](04_MERGE_GOVERNANCE.md)
- [Mathematical Function Governance](MATHEMATICAL_FUNCTION_GOVERNANCE.md)
- [Dogfood PR Audit](17_DOGFOOD_PR_AUDIT.md)
- [Scientific Validation Report](SCIENTIFIC_VALIDATION_REPORT.md)
- [Industrial Validation Report](INDUSTRIAL_VALIDATION_REPORT.md)
