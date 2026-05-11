# 16 — AFJG Coding Copilot Simulator

## لماذا البرمجة أفضل اختبار صناعي أول

البرمجة تقدم بيئة قابلة للقياس: issue واضح، patch واضح، اختبارات قابلة للتنفيذ، CI قابل للتحقق، وPR يترك أثرًا كاملًا للتدقيق. لهذا فهي مسار أدق من محاولة محاكاة العقل الإنساني العام في البداية.

## خريطة AFJG إلى سياق البرمجة

- **Reality** = حالة المستودع + نص الـ issue + حالة الاختبارات
- **Distinction** = تصنيف المهمة وتحديد الملفات والدعاوى
- **Concept** = مفاهيم الكود والعقود الطبقية
- **Claim** = دعوى الـ patch (مثلاً fixes_bug)
- **Evidence** = tests + static checks + architecture checks + CI
- **Judgment** = ZERO / HYPOTHESIS / CERTIFICATE
- **ReverseTrace** = issue → claim → patch → tests → result → PR

## الفرق عن Copilot التقليدي

Copilot التقليدي يقترح كودًا.  
AFJG Coding Copilot يحكم على صحة المقترح وفق الدليل والحوكمة قبل أي شهادة.

- Proposal alone ≠ evidence.
- Summary alone ≠ proof.
- PASS/FAIL ليست أحكامًا معرفية نهائية.
- MERGED ليست حكمًا معرفيًا نهائيًا.

## نقد المنهجية في السياق البرمجي

- يجب تخصيص AFJG لعمليات البرمجة بدل إبقائه بصياغة ذهنية عامة واسعة.
- الإفراط في التجريد قد يبطئ التطوير في التغييرات منخفضة المخاطر.
- الأدلة التنفيذية (tests/CI) يجب أن تبقى مركزية.
- نجاح الاختبارات لا يعني حقيقة مطلقة؛ الشهادة تبقى محكومة بالنطاق والأثر والتتبع.

## مبادئ الحوكمة في هذا الهيكل

- المخرجات النهائية العامة محصورة في: `zero | hypothesis | certificate`.
- `suspend` إن ظهر فهو داخلي ويُطوى عند الحدود العامة إلى `hypothesis` أو `zero`.
- لا شهادة بدون:
  - claim واضح
  - evidence مناسب للنطاق
  - architecture check ناجح
  - reverse trace مكتمل
- أي architecture violation أو unlinked patch file يُسقط الحكم إلى ZERO.
- غياب الأدلة أو انتظار CI يبقي الحكم HYPOTHESIS.

## المسار التجاري المقترح

1. PR Auditor
2. CI Governance Bot
3. Copilot Review Assistant
4. Enterprise AI Coding Trust Layer
5. Regulated-code Assistant
