# MATHEMATICAL FUNCTION GOVERNANCE

## 1) لماذا F(U) ليست schema فقط
الصيغة `F(U)=⟨N,V,R,O,E,C,P,T,Z⟩` تعرّف مكونات الوحدة، لكنها وحدها لا تكفي لضبط الانتقال بين المستويات. الحوكمة تضيف القوانين التي تمنع الانحراف البنيوي وتربط كل نتيجة بمصدرها.

## 2) ما هي levels
تم تعريف سلسلة مستويات معرفية من الواقع حتى الجواب النهائي والنمط المتبقي:
L0_REALITY → L1_UNICODE → ... → L15_FINAL_ANSWER → L16_RESIDUAL_PATTERN.

## 3) ما هي morphisms
كل انتقال بين مستويين يحتاج Morphism مسجلًا في `LevelMorphismRegistry` مع شروط حفظ (trace/relation/evidence_need/certainty_cap/residual) ومنع آثار محظورة (خلق دليل، إصدار شهادة، رفع يقين دون دليل، محو residual).

## 4) كيف نربط السابق باللاحق
`GovernedFractalUnit` يفرض ربطًا صريحًا عبر:
- `pre_unit_ids`
- `post_unit_ids`
- `morphism_in` / `morphism_out`
- `trace_refs`

ولا تُقبل الوحدة في السلسلة النهائية بدون هذا الربط.

## 5) ما هي OperatorAlgebra
`OperatorAlgebra` يعرّف تركيب المشغلات وقوانين الهوية والتركيب، ويمنع:
- اعتبار emphasis دليلًا
- اعتبار murab يقينًا واقعيًا
- اعتبار mushtaq برهان حدث
- اعتبار مخرجات الأدوات/GPT دليلًا

## 6) ما هي Fold/Unfold/Refold laws
قوانين `FoldUnfoldRefoldLaws` تتحقق من:
- عدم رفع اليقين بالطي وحده
- حفظ evidence_need
- حفظ residuals
- استرجاع العلاقات الأساسية عند unfold
- استقرار refold score المستهدف ≥ 0.95

## 7) ما هي Jami/Mani metrics
`JamiManiCalculator` يحسب:
- `jami_score` = تغطية الإيجابي
- `mani_score` = استبعاد السلبي
- `concept_tightness` = المتوسط التوافقي بينهما

## 8) كيف ترتبط بيانات PR #51 بهذه الحوكمة
`DatasetMathAnnotator` يضيف/يتحقق من الحقول الرياضية لكل مثال (level, morphism, invariants, certainty_cap, residual_if_failed) بدل الاكتفاء بوسم عام.

## 9) كيف تمنع الحوكمة تضخم الطبقات
`MathematicalGovernanceGate` يجمع نتائج المورفيزمات والمشغلات والطي والـJami/Mani وتعليق البيانات في تقرير واحد مع score وحد أدنى للقبول.

## 10) كيف تجعل الدالة الرياضية عقل المشروع
عند تطبيق السلسلة:
`Level → Morphism → Operator → Conservation → Evidence → Certainty → Proof → Residual`
تصبح كل مخرجات النظام قابلة للتتبع والتفسير، ويُمنع إصدار Certificate خارج المسار الحاكم.
