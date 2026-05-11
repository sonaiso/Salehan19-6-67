# 17 — Dogfood PR Audit (AFJG Coding Copilot)

## لماذا هذه المرحلة

PR #58 يمثل تقدمًا هندسيًا قويًا لأنه نقل AFJG من وصف منهجي إلى نواة حكم برمجي قابلة للاختبار.  
PR #59 أضاف تدقيق PRs واقعية (`#56`, `#57`, `#58`) وأثبت عمليًا أن `MERGED != CERTIFICATE` وأن `3/4 checks != CERTIFICATE`.

## قاعدة الحوكمة الأساسية

- `MERGED` حالة مستودع، وليست حكمًا معرفيًا.
- حالة CI هي دليل تنفيذي، وليست الحكم النهائي.
- أي `checks_pending > 0` يفرض `HYPOTHESIS` مع residual من نوع `ci_pending` و`merge_with_pending_checks`.
- المرور الكامل للـ checks شرط لازم للشهادة، لكنه غير كافٍ وحده.

## لماذا PR #58 و PR #59 يبقيان HYPOTHESIS

عند وجود 3/4 checks فقط:

- لا يمكن اعتبار الحوكمة مكتملة.
- لا يُسمح بترقية الحكم إلى `CERTIFICATE`.
- الحكم الصحيح هو `HYPOTHESIS` بسبب `ci_pending`.

PR #59 أصبح أيضًا حالة self-audit مهمة:

- تم دمجه مع check pending.
- يظل حكمه المعرفي `HYPOTHESIS` حتى بعد الدمج.
- residual الإضافي هو `merge_with_pending_checks`.

## كيف يتم التدقيق الآن

Dogfood audit يحمّل fixtures محلية لـ PRs حقيقية (`#56`, `#57`, `#58`, `#59`) من:

`examples/coding_copilot/real_prs/`

ثم يطبق قواعد الحوكمة:

1. لا Pending checks
2. لا Failed checks مطلوبة
3. كل checks المطلوبة خضراء
4. ReverseTrace مكتمل
5. لا residual blocking/fatal
6. claim/evidence متطابقة

## أثر هذه المرحلة

هذه المرحلة تثبت أن AFJG يحاكم PRs الخاصة بالمشروع نفسه بدل الاعتماد على ملخصات توليدية.  
المنهجية تصبح قابلة للتحقق الذاتي: هندسة التقدم شيء، والحكم المعرفي المصدق شيء آخر.
