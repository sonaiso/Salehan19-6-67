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

### خط الأنابيب — 21 طبقة مرتبة في 5 مجموعات

الطبقات الـ21 مصنّفة في 5 مجموعات وظيفية. كل مجموعة يجب أن تكتمل قبل أن تبدأ المجموعة التالية.

#### المجموعة 1: Epistemic Existence (طبقات 1–2)
تؤسس ما يوجد حقًا وتفصل المعلومة الموثقة عن الرأي السابق.

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 1 | `reality_grounding_layer` | Reality Grounding |
| 2 | `prior_opinion_filter_layer` | Prior Opinion Filter |

#### المجموعة 2: Semantic-Relational (طبقات 3–8)
تبني البنية الدلالية العلائقية. **شرط لازم:** يجب إتمامها قبل بدء أي طبقة بيانية لغوية ولا سيما قبل تشكيل الحكم.

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 3 | `differentiation_layer` | Differentiation |
| 4 | `essence_assignment_layer` | Essence Assignment ← مطلوب قبل تشكيل الحكم |
| 5 | `domain_assignment_layer` | Domain Assignment ← مطلوب قبل تشكيل الحكم |
| 6 | `relational_mapping_layer` | Relational Mapping (13 أنواع نسب) ← مطلوب قبل تشكيل الحكم |
| 7 | `arabic_operator_layer` | Arabic Operator Parsing (17 فئة) |
| 8 | `binding_layer` | Binding |

#### المجموعة 3: Bayani-Linguistic (طبقات 9–15)
تبني الاستدلال البياني اللغوي. لا تبدأ إلا بعد إتمام المجموعة 2.

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 9 | `concept_formation_layer` | Concept Formation |
| 10 | `judgment_formation_layer` | Judgment Formation |
| 11 | `signifier_analysis_layer` | Signifier Analysis |
| 12 | `signified_analysis_layer` | Signified Analysis |
| 13 | `signifier_signified_relation_layer` | Signifier-Signified Relation |
| 14 | `mantuq_layer` | Mantuq Analysis |
| 15 | `mafhoom_layer` | Mafhoom Analysis |

#### المجموعة 4: Usuli-Application (طبقات 16–20)
تطبق قواعد أصول الفقه وتنزّل الحكم. **شرط لازم:** لا تنزيل قبل تحقيق المناط.

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 16 | `general_specific_layer` | General/Specific |
| 17 | `absolute_restricted_layer` | Absolute/Restricted |
| 18 | `causal_juridical_relations_layer` | Causal-Juridical Relations |
| 19 | `tahqeeq_manat_layer` | Tahqeeq al-Manat ← مطلوب قبل التنزيل |
| 20 | `application_layer` | Application |

#### المجموعة 5: Audit (طبقة 21)
المراجعة النهائية وإنتاج خريطة اليقين.

| الرتبة | المفتاح | الاسم |
|-------|---------|-------|
| 21 | `epistemic_audit_layer` | Epistemic Audit |

### ثوابت خط الأنابيب

- `NoLevelSkipInPipeline` — لا تجاوز طبقة قبل اكتمال مخرجاتها
- `NoJudgmentBeforeEssenceAssignment` — لا حكم قبل تعيين الذات
- `NoBayaniLinguisticBeforeSemanticRelationalComplete` — لا تبدأ المجموعة البيانية قبل اكتمال المجموعة الدلالية
- `NoJudgmentFormationBeforeEssenceDomainRelationsResolved` — لا تشكيل حكم (طبقة 10) قبل إتمام طبقات 4 و5 و6
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

## Bayani Relational Parser v0.2

يضيف إصدار v0.2 محلل النسب البياني — طبقة تستخرج البنى الدلالية-العلائقية من نصوص اللغة العربية **قبل** تشكيل أي حكم.

### الوظيفة الأساسية

يحوّل المحلل النص المدخل إلى هيكل نسبي منظم يكشف عن:

- **نوع النسبة** — واحدة من 13 نسبة: إسنادية، تضمينية، تقييدية، فاعلية، مفعولية، سببية، مسببية، شرطية، غائية، زمانية، مكانية، حالية، استثنائية.
- **العامل الحامل** — الأداة النحوية أو اللغوية التي حملت النسبة (مثل `nominal_sentence`، `verb_sentence`، `conditional_tool`، `exception_tool`، `ghayah_tool`، `hal`، `cause_tool`).
- **الرتبة المعرفية** — قطعي أو ظني.
- **الأثر الأصولي المحتمل** — مثل `possible_mafhoom_sifah`، `takhsis_candidate`، `illah_candidate`.
- **قفزات محظورة مُراجَعة** — مثل `NoJudgmentFormationBeforeEssenceDomainRelationsResolved`.

### القاعدة الحاكمة

> لا حكم قبل حل النسب. لا نسبة بلا عامل حامل.

### التكامل مع خط الأنابيب

- **الطبقة 6 — relational_mapping_layer**: تستدعي `parse_relations()` وتُرفق أنواع النسب وعواملها في `claims` الطبقة. تُسجَّل النسب غير المحلولة في `uncertainties`.
- **الطبقة 7 — arabic_operator_layer**: تعرض قيم `carrier_operator` المستخرجة في `claims` لضمان توثيق علاقات العامل والمعمول.
- **الثابت الجديد NoRelationWithoutCarrier**: يرفض المحقق (audit) أي نسبة لا يحملها عامل موثق.

### تشغيل الاختبارات

```bash
python -m pytest tests/test_mustadil_runtime.py tests/test_bayani_relational_parser.py -v
python tests/verify_bayani_repository.py
```

## Epistemic Cognitive Decoder v0.3

يضيف إصدار v0.3 **الديكودر المعرفي** — طبقة محاكاة قرار معرفية مبنية فوق النموذج اللغوي تفرض عليه سلسلة التحقق:

```text
واقع → حس/مصدر → معلومات → ربط → فكر → مطابقة → دليل → درجة يقين → جواب
```

### ملفات MVP (5 ملفات)

| الملف | المحتوى |
|-------|---------|
| `bayani/epistemic_decoder/ontology.yaml` | واقع، حس، معلومات، ربط، فكر، مفهوم، يقين |
| `bayani/epistemic_decoder/semiotics.yaml` | دال، مدلول، مطابقة، تضمن، التزام، كلي، جزئي |
| `bayani/epistemic_decoder/relations.yaml` | إسناد، تقييد، تضمين، سبب، مسبب، علة، قياس |
| `bayani/epistemic_decoder/decoder_policy.md` | قواعد السماح والمنع المعرفي |
| `run_decoder.py` | يشغّل الديكودر المعرفي + التحقق + إخراج الجواب |

### معمارية الوحدات السبع

| الوحدة | الاسم | الوظيفة |
|--------|-------|---------|
| 1 | `InputAnalyzer` | تصنيف نوع المهمة، المجال، خطر الهلوسة |
| 2 | `RealityExtractor` | استخراج الواقع موضوع السؤال |
| 3 | `SemioticParser` | تفكيك الدال والمدلول |
| 4 | `RelationGraphBuilder` | بناء شبكة العلاقات الدلالية |
| 5 | `EvidenceRetriever` | استرجاع الأدلة والمصادر |
| 6 | `CertaintyScorer` | حساب درجة اليقين المعرفي |
| 7 | `AnswerDecoder` | تأليف الجواب المضبوط |

### معادلة اختيار الجواب

```text
AnswerScore =
  0.20 x LinguisticCoherence
+ 0.25 x RealityMatch
+ 0.20 x EvidenceStrength
+ 0.15 x SemanticValidity
+ 0.10 x InferenceValidity
+ 0.10 x CertaintyClarity
- 0.30 x HallucinationRisk
```

الحد الأدنى للسماح بالجواب: `AnswerScore >= 0.60`.

### استخدام سريع

```python
from bayani.epistemic_decoder import EpistemicCognitiveDecoder

decoder = EpistemicCognitiveDecoder()
output = decoder.decode("ما الفرق بين العلم والثقافة؟", reasoning_effort="high")
print(output.final_answer)
print(output.certainty_level)
print(output.answer_score)
```

أو عبر سطر الأوامر:

```bash
python run_decoder.py "ما الفرق بين العلم والثقافة؟" --verbose
python run_decoder.py "هل المفاهيم مرتبطة بالواقع؟" --effort xhigh --json
```

### تشغيل اختبارات الديكودر المعرفي

```bash
python -m pytest tests/test_epistemic_decoder.py -v
```

