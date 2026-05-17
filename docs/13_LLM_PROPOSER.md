# 13 — Governed LLM Proposer (AFJG-controlled)

## الأطروحة (Core Thesis)

> **LLMs propose; AFJG governs judgment.**

هذه الوحدة تحوّل الأطروحة المُعلنة في `README.md` (السطر 21) من نص نظري إلى منتج قابل للتشغيل والاختبار.

---

## لماذا مخرج LLM يبدأ كـ HYPOTHESIS؟

وفق القانون الحاكم `AGENTS.md` والانتقالات المحظورة:

```text
model_output_as_evidence          → محظور (مخرج النموذج ليس دليلاً)
tool_output_as_certificate_without_governance → محظور
certificate_without_proof_object  → محظور
certificate_without_governance_gate → محظور
certificate_without_reverse_trace → محظور
```

**اللغة الكبيرة تُولِّد ادعاءات — لا براهين.**  
أي مخرج LLM يدخل مسار الحوكمة بافتراض `HYPOTHESIS` ولا يرتقي إلا بعد:
1. اجتياز جميع بوابات AFJG الموجودة
2. وجود دليل خارجي حقيقي (`evidence != []`)
3. وجود سجل عكسي كامل (`reverse_trace != []`)
4. لا انتهاكات (`violated_rules == []`)

---

## أحكام AFJG الثلاثة النهائية

```text
ZERO        = fatal violation or invalid proof path
HYPOTHESIS  = plausible structure with incomplete evidence
CERTIFICATE = evidence + governance + reverse trace completed
```

**لا يُسمح بحكم رابع.** أي محاولة لإنشاء `GovernedAnswer(verdict="MERGED")` ترفع `ValueError` فوراً.

---

## كيف يصل إلى CERTIFICATE؟

```
LLM output (Proposal)
    ↓
Gate 1: Emptiness gate          → ZERO  if prompt is empty
Gate 2: Contradiction gate      → ZERO  if contradiction claim without evidence
Gate 3: Nabhani rational gate   → ZERO  if RationalMethodJudge.judge() = "rejected"
                                  (soft warnings → trace only, not blocking)
Gate 4: Evidence gate           → HYPOTHESIS if evidence == [] OR reverse_trace == []
Gate 5: Certificate gate        → CERTIFICATE if evidence != [] AND reverse_trace != []
                                              AND violated_rules == []
```

### القاعدة الصارمة

```text
MERGED != CERTIFICATE
3/4 checks != CERTIFICATE
```

كل البوابات يجب أن تمر. بوابة واحدة ناقصة → `HYPOTHESIS` كحد أقصى.

---

## البوابات المستدعاة من المستودع

| البوابة | المصدر في المستودع |
|---|---|
| RationalMethodJudge | `src/mcd/nabhani/rational_method_judge.py` |

البوابة تفحص (من منهج النبهاني):
- `target_reality` — واقع الادعاء
- `evidence` — الدليل الخارجي
- `sense_source` — مصدر الحس
- `prior_information` — المعلومات السابقة
- `relation_chain` — سلسلة الربط
- `correspondence_test` — اختبار المطابقة
- `certainty` — درجة اليقين

---

## أمثلة CLI

```bash
# HYPOTHESIS (بدون دليل)
python -m mcd.llm_proposer --provider echo --prompt "النار محرقة"
# → exit code 1

# HYPOTHESIS (دليل موجود، لا trace)
python -m mcd.llm_proposer --provider echo --prompt "ادعاء" \
    --evidence "دليل 1" --evidence "دليل 2"
# → exit code 1

# ZERO (ادعاء تناقضي)
python -m mcd.llm_proposer --provider echo --prompt "ادعاء مستحيل"
# → exit code 2

# إعادة تشغيل artifact
python -m mcd.llm_proposer --replay artifacts/llm_proposer/xxx.json
```

رموز الخروج: `0` → CERTIFICATE, `1` → HYPOTHESIS, `2` → ZERO

---

## مثال Python End-to-End

```python
from mcd.llm_proposer import GovernedProposalPipeline, AFJGGovernor, EchoProposer

proposer = EchoProposer()
governor = AFJGGovernor()
pipeline = GovernedProposalPipeline(proposer, governor)

# ادعاء بدون دليل → HYPOTHESIS دائماً
answer = pipeline.run("النار محرقة")
assert answer.verdict == "HYPOTHESIS"

# ادعاء مع دليل كامل وسجل عكسي → CERTIFICATE
answer = pipeline.run(
    "النار محرقة",
    evidence=["تجربة 1: اللمس بالنار", "تجربة 2: قياس الحرارة"],
    reverse_trace=["الخطوة 1: صياغة الادعاء", "الخطوة 2: جمع الأدلة"],
)
assert answer.verdict == "CERTIFICATE"
assert answer.violated_rules == []
```

---

## حفظ وإعادة تشغيل الأثر

```python
from mcd.llm_proposer import trace as trace_module, AFJGGovernor

# يحفظ إلى artifacts/llm_proposer/<timestamp>_CERTIFICATE.json
path = trace_module.save(answer)

# إعادة التشغيل — نفس الحكم حتمياً مع EchoProposer
governor = AFJGGovernor()
replayed = trace_module.replay(path, governor)
assert replayed.verdict == answer.verdict
```

---

## المراجع

- `src/mcd/llm_proposer/` — الكود الكامل
- `tests/llm_proposer/` — 62 اختبار (8 ملفات)
- `src/mcd/nabhani/rational_method_judge.py` — البوابة الحاكمة الأساسية
- `docs/03_JUDGMENT_MODEL.md` — نموذج الأحكام
- `docs/04_MERGE_GOVERNANCE.md` — حوكمة الدمج
- `AGENTS.md` — القانون الحاكم
