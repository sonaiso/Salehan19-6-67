# Salehan19-6-67

يوفر هذا المستودع طبقة مواصفة وتحقق لمشروع **Bayani Knowledge System**. الحالة الحالية هي مواصفة JSON قابلة للقراءة الآلية، ومخطط JSON Schema، وبرومبتات حاكمة، واختبارات تحقق مستودعية. لا يحتوي هذا المستودع حاليًا على تنفيذ runtime لمحركات Laravel أو Neo4j أو محركات الاستدلال.

تصف المواصفة بنية قابلة للتحويل مستقبلًا إلى:

- JSON Schema
- Laravel Models
- Neo4j Graph
- Test Cases
- Proof Layer

## الملفات

- `/schema/bayani-knowledge-system.schema.json`: مخطط JSON Schema للنظام.
- `/spec/bayani-knowledge-system.json`: المثال المرجعي الذي يجمع النواة الرسمية، قاعدة المعرفة السابقة، الأنطولوجيا، طبقات النحو والاستدلال، الاختبارات، وطبقة البرهان، وخط أنابيب المستدل.
- `/docs/prompts/nabhani-mustadil-readiness.prompt.md`: برومبت جاهزية المستدل الذي يضبط المخرجات على `Certificate | Hypothesis | Zero` دون تعديل المواصفة أو المخطط.
- `/docs/prompts/mustadil-decoder-pipeline.prompt.md`: برومبت خط أنابيب المستدل الذي يحكم الـ21 طبقة المرتبة من الواقع إلى الحكم المدقق.
- `/tests/verify_bayani_repository.py`: بوابات تحقق مستودعية تفحص صلاحية JSON، توافق المواصفة مع المخطط، روابط README، أقسام البرومبتات، وثوابت البرهان والملكة وخط الأنابيب.

## الملامح التي تغطيها المواصفة

- النواة الرسمية: `S + D + T + E + Z + C + R + P`
- قاعدة المعرفة السابقة ووحدات المعرفة مع مصادر موثقة ومؤهلة
- الأنطولوجيا العليا ومثال حدث الكتابة
- قواعد العامل والقرينة والحذف والإحالة
- التعارض والترجيح وربط المستويات بعلاقة `R(level_n, level_n+1)`
- تحليل إجابات GPT إلى مرشحات ثم دعاوى وعلاقات وأدلة وبيان ومبين وبرهان قبل إصدار الشهادة
- التوثيق والتعلّم والاختبارات وطبقة البرهان
- توثيق معماري للكيانات العليا، ونماذج Laravel، وعلاقات Neo4j، ومراحل التنفيذ المستقبلية دون تنفيذ runtime في هذا المستودع

## منهجية قياس الملكة

تضيف المواصفة طبقة `malakah_methodology` لقياس الملكة بوصفها قدرة استعمال القاعدة في محلها، لا مجرد حفظ القاعدة. تغطي الطبقة آلات قابلية التطبيق، تحقيق المناط، تصنيف الملكات الفرعية، تزاحم القواعد، الاستثناءات، نمو الملكة، تحليل السؤال، منع الرأي السابق، توليد المرشحات، تصنيف الأخطاء، العتبات، الاختبارات التدرجية والخادعة، الذاكرة، سلامة الطبقات، تغطية invariants التنفيذية، توقع الفشل، ضبط التوسع، وقياس أهلية المستدل.

القاعدة الحاكمة: لا تسمح أي درجة ملكة وحدها بإصدار Certificate؛ الشهادة تحتاج ProofObject صالحًا، وغياب `blocking_zero`، وتحقق محل القاعدة، وربطًا بدليل قابل للتتبع.

## برومبت أهلية المستدل

أضيف ملف `docs/prompts/nabhani-mustadil-readiness.prompt.md` بوصفه البرومبت الحاكم لطبقة **Mustadil Readiness**. يربط البرومبت النواة الرسمية `S + D + T + E + Z + C + R + P` بشرط أهلية المستدل قبل الجواب، فلا يسمح بتحويل أي نتيجة إلى `Certificate` إلا بعد تحقق الدليل، وغياب الصفر المانع، وصحة `ProofRank`، واكتمال `reverse_trace`.

ترتبط هذه الطبقة داخل المواصفة بـ `answer_analysis_engine` و`malakah_methodology` و`mustadil_competence_score` و`proof_gate` و`ZeroGuard` و`reverse_trace`، وتبقي المخرجات النهائية محصورة في:

- `Certificate`
- `Hypothesis`
- `Zero`

## عقل المستدل لديكودر GPT-5.5

تضيف المواصفة طبقة `mustadil_decoder_pipeline` وهي طبقة رقابية فوق الديكودر اللغوي تحول النموذج من:

```text
سياق → توقع الكلمة التالية → جواب
```

إلى:

```text
واقع/نص → تمييز → تعيين → نسب → ربط → مفهوم → حكم → لفظ مضبوط
```

### القاعدة الذهبية

> لا حكم بلا محل، ولا محل بلا تمييز، ولا تمييز بلا تعيين، ولا تعيين بلا نسب، ولا نسب بلا عوامل، ولا ربط بلا معلومات، ولا مفهوم بلا واقع، ولا تنزيل بلا تحقيق مناط.

### خط الأنابيب — 21 طبقة مرتبة

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 1 | `reality_grounding_layer` | Reality Grounding |
| 2 | `prior_opinion_filter_layer` | Prior Opinion Filter |
| 3 | `differentiation_layer` | Differentiation |
| 4 | `essence_assignment_layer` | Essence Assignment |
| 5 | `domain_assignment_layer` | Domain Assignment |
| 6 | `relational_mapping_layer` | Relational Mapping (13 أنواع نسب) |
| 7 | `arabic_operator_layer` | Arabic Operator Parsing (17 فئة) |
| 8 | `binding_layer` | Binding |
| 9 | `concept_formation_layer` | Concept Formation |
| 10 | `judgment_formation_layer` | Judgment Formation |
| 11 | `signifier_analysis_layer` | Signifier Analysis |
| 12 | `signified_analysis_layer` | Signified Analysis |
| 13 | `signifier_signified_relation_layer` | Signifier-Signified Relation |
| 14 | `mantooq_layer` | Mantooq Analysis |
| 15 | `mafhoom_layer` | Mafhoom Analysis |
| 16 | `general_specific_layer` | General/Specific |
| 17 | `absolute_restricted_layer` | Absolute/Restricted |
| 18 | `causal_juridical_relations_layer` | Causal-Juridical Relations |
| 19 | `tahqeeq_manat_layer` | Tahqeeq al-Manat |
| 20 | `application_layer` | Application |
| 21 | `epistemic_audit_layer` | Epistemic Audit |

### ثوابت خط الأنابيب

- `NoLevelSkipInPipeline` — لا تجاوز طبقة قبل اكتمال مخرجاتها
- `NoJudgmentBeforeEssenceAssignment` — لا حكم قبل تعيين الذات
- `NoApplicationWithoutTahqeqManat` — لا تنزيل قبل تحقيق المناط
- `NoPriorOpinionAsEvidence` — لا رأي سابق في مقام الدليل
- `NoMafhumStrongerThanMantuq` — لا يتجاوز المفهوم قوة المنطوق
- `NoIllahWithoutValidation` — لا علة قبل اختبارات العلة السبعة
- `NoDomainTransferWithoutBridge` — لا انتقال مجالي بلا جسر

يصف البرومبت الحاكم لهذه الطبقة ملف `docs/prompts/mustadil-decoder-pipeline.prompt.md`.

## التحقق

يتحقق مسار CI من صلاحية JSON Schema، ومطابقة `spec/bayani-knowledge-system.json` للمخطط، وسلامة روابط Markdown، ووجود أقسام البرومبتات الحاكمة، وحصر مخرجات طبقة أهلية المستدل في الثلاثية المعتمدة، وتغطية اختبارات المواصفة لحالات `Certificate` و`Hypothesis` و`Zero`، وسلامة خط أنابيب المستدل وترتيب طبقاته وثوابته.

يمكن تشغيل بوابات التحقق محليًا عبر:

```bash
python -m pip install jsonschema==4.25.1
python tests/verify_bayani_repository.py
```

