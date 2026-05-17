# LLM Proposer — Governed LLM Output via AFJG

## الأطروحة (Core Thesis)

> **LLMs propose; AFJG governs judgment.**

اللغة الكبيرة تولّد **اقتراحاً** (Proposal) — لا حكماً. أيُّ مخرج LLM يدخل مسار الحوكمة بافتراض **`HYPOTHESIS`** ولا يرتقي إلى **`CERTIFICATE`** إلا بعد اجتياز جميع بوابات AFJG مع وجود دليل كامل وسجل عكسي قابل للتحقق.

---

## لماذا مخرج LLM يبدأ كـ HYPOTHESIS؟

وفق `AGENTS.md` والقانون الحاكم:

- `model_output_as_evidence` — **انتقال محظور**. مخرج النموذج ليس دليلاً.
- `tool_output_as_certificate_without_governance` — **محظور**. لا شهادة بدون بوابة حوكمة.

أي مخرج LLM هو في الأصل ادعاء (claim) يحتاج إلى:
1. واقع قابل للتحقق (target_reality)
2. دليل خارجي (evidence)
3. سجل عكسي كامل (reverse_trace)
4. اجتياز جميع بوابات AFJG

---

## شروط الوصول إلى CERTIFICATE

CERTIFICATE يتطلب **الثلاثة معاً** (لا يمكن تخطي أيٍّ منها):

| الشرط | الوصف |
|---|---|
| `evidence != []` | دليل خارجي حقيقي (ليس مخرج النموذج) |
| `reverse_trace != []` | سجل عكسي من المدقق الخارجي |
| `violated_rules == []` | لا انتهاكات لقواعد AFJG |

أي فشل → `HYPOTHESIS`. تناقض داخلي أو مخالفة صريحة → `ZERO`.

---

## بنية الوحدة

```
src/mcd/llm_proposer/
├── __init__.py            # واجهة عامة
├── __main__.py            # نقطة دخول python -m mcd.llm_proposer
├── README.md              # هذا الملف
├── types.py               # Proposal, GovernedAnswer, Verdict
├── base.py                # BaseLLMProposer (abstract)
├── providers/
│   ├── __init__.py
│   ├── echo.py            # EchoProposer (حتمي، لا يحتاج API)
│   ├── openai_proposer.py # OpenAIProposer (اختياري)
│   └── anthropic_proposer.py # AnthropicProposer (اختياري)
├── governor.py            # AFJGGovernor — البوابات الحاكمة
├── pipeline.py            # GovernedProposalPipeline
├── trace.py               # حفظ وإعادة تشغيل الأثر
└── cli.py                 # واجهة سطر الأوامر
```

---

## البوابات الحاكمة الموجودة فعلاً

`AFJGGovernor` يستدعي البوابات التالية من المستودع:

| البوابة | المصدر | الوصف |
|---|---|---|
| Emptiness gate | `governor.py` | proposal prompt فارغ → ZERO |
| Contradiction gate | `governor.py` | ادعاء تناقضي بدون دليل → ZERO |
| Nabhani rational gate | `src/mcd/nabhani/rational_method_judge.py` | `RationalMethodJudge.judge()` — يفحص: واقع + حس + سابق + ربط + مطابقة + دليل + يقين |
| Evidence gate | `governor.py` | لا دليل أو لا trace → HYPOTHESIS |
| Certificate gate | `governor.py` | كل البوابات + evidence + trace → CERTIFICATE |

---

## أمثلة CLI

```bash
# HYPOTHESIS (بدون دليل)
python -m mcd.llm_proposer --provider echo --prompt "النار محرقة"

# HYPOTHESIS (دليل موجود، لا trace)
python -m mcd.llm_proposer --provider echo --prompt "ادعاء" \
    --evidence "دليل 1" --evidence "دليل 2"

# ZERO (ادعاء فارغ)
python -m mcd.llm_proposer --provider echo --prompt ""

# إعادة تشغيل artifact
python -m mcd.llm_proposer --replay artifacts/llm_proposer/xxx.json

# حفظ الأثر
python -m mcd.llm_proposer --provider echo --prompt "ادعاء" --save
```

رموز الخروج:
- `0` → CERTIFICATE
- `1` → HYPOTHESIS
- `2` → ZERO

---

## مثال Python End-to-End

```python
from mcd.llm_proposer import GovernedProposalPipeline, AFJGGovernor, EchoProposer

# إعداد المسار
proposer = EchoProposer()
governor = AFJGGovernor()
pipeline = GovernedProposalPipeline(proposer, governor)

# ادعاء بدون دليل → HYPOTHESIS
answer = pipeline.run("النار محرقة")
assert answer.verdict == "HYPOTHESIS"

# ادعاء مع دليل كامل وسجل عكسي → CERTIFICATE
answer = pipeline.run(
    "النار محرقة",
    evidence=["تجربة 1: اللمس", "تجربة 2: القياس"],
    reverse_trace=["الخطوة 1: صياغة الادعاء", "الخطوة 2: جمع الأدلة"],
)
assert answer.verdict == "CERTIFICATE"
assert answer.violated_rules == []
```

---

## حفظ وإعادة تشغيل الأثر

```python
from mcd.llm_proposer import trace as trace_module, AFJGGovernor

# حفظ
path = trace_module.save(answer)

# إعادة تشغيل (نفس الحكم حتمياً مع EchoProposer)
governor = AFJGGovernor()
replayed = trace_module.replay(path, governor)
assert replayed.verdict == answer.verdict
```

---

## القيود الصارمة

- ❌ `MERGED != CERTIFICATE` — merge لا يساوي شهادة
- ❌ `3/4 checks != CERTIFICATE` — أي بوابة ناقصة → HYPOTHESIS
- ❌ لا حكم رابع — `ValueError` فوري لأي verdict خارج الثلاثة
- ✅ مخرج LLM = HYPOTHESIS دائماً حتى إثبات العكس
