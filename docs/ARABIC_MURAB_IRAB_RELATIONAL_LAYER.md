# Arabic Mu'rab / I'rab Relational Engineering Layer
# طبقة هندسة المعربات والإعراب العلاقي في العربية

**Phase 7.5 — MCD (Minimal Cognitive Decoder)**

---

## 1. لماذا المعربات طبقة علاقية؟

الإعراب في العربية ليس مجرد حركات تُلفظ. الإعراب هو **نظام إسقاط علاقي**: يكشف موقع كل كلمة في شبكة العلاقات النحوية والدلالية داخل الجملة.

الجملة العربية هي graph معرفي. كل كلمة معربة هي عقدة في هذا الـ graph، وعلامتها الإعرابية هي مؤشر على نوع الحافة (edge) التي تربطها بسائر العقد.

```
جاءَ زيدٌ
       ↑
فاعل (agent_of) ← زيد ← nominative ← damma
```

The I'rab layer maps: Surface → Marker → Case → Role → Semantic Relation → Graph Edge.

---

## 2. الفرق بين الحركة والعلاقة

| الحركة | العلاقة |
|--------|---------|
| الضمة | قد تكون: فاعل / مبتدأ / خبر / اسم كان / خبر إن |
| الفتحة | قد تكون: مفعول به / حال / تمييز / خبر كان / ظرف |
| الكسرة | قد تكون: مجرور بحرف / مضاف إليه / تابع مجرور |
| السكون | قد يكون: فعل مضارع مجزوم / فعل شرط / جواب شرط |

**القاعدة الحاكمة**: الحركة تشير إلى الموقع الإعرابي، لكن العلاقة تُحدَّد بالعامل والتركيب والسياق.

---

## 3. العامل والمعمول

كل علامة إعراب لها **عامل** أوجبها:

| العامل | الحكم الإعرابي |
|--------|---------------|
| الفعل | يرفع الفاعل، ينصب المفعول |
| حرف الجر | يجر الاسم |
| إنَّ وأخواتها | تنصب الاسم، ترفع الخبر |
| كان وأخواتها | ترفع الاسم، تنصب الخبر |
| لم / لا الناهية | تجزم المضارع |
| لن / أن / كي | تنصب المضارع |
| الإضافة | تجر المضاف إليه |

العامل مذكور أو مقدَّر. إذا كان مقدَّرًا: `governing_factor_id = inferred, inferred=True`.

---

## 4. الرفع والنصب والجر والجزم

### الرفع (Nominative)
يكشف مواقع: الفاعل، نائب الفاعل، المبتدأ، الخبر، اسم كان، خبر إن، الفعل المضارع غير المتأثر بناصب أو جازم.

### النصب (Accusative)
يكشف مواقع: المفعول به، المفعول المطلق، المفعول لأجله، المفعول فيه، الحال، التمييز، المستثنى، خبر كان، اسم إن، الفعل المضارع بعد ناصب.

### الجر (Genitive)
يكشف مواقع: الاسم بعد حرف جر، المضاف إليه، التابع المجرور.

### الجزم (Jussive)
يكشف مواقع: الفعل المضارع بعد جازم (لم، لا الناهية، إن الشرطية، من الشرطية...)، فعل الشرط، جواب الشرط.

---

## 5. العلامات الأصلية والفرعية والمقدرة

| النوع | الوصف | مثال |
|-------|-------|------|
| أصلية | الحركات الأصلية: ضمة، فتحة، كسرة، سكون | زيدٌ (ضمة)، الدرسَ (فتحة) |
| فرعية | علامة نيابية: واو، ألف، ياء، نون، ألف كسر | أبوك (واو)، طالبان (ألف) |
| مقدرة | لا تظهر: للتعذر أو الثقل أو المناسبة | الفتى (ضمة مقدرة) |
| محلية | المبني في موضع إعراب | هو (في محل رفع) |

---

## 6. كيف يكشف الإعراب الفاعلية والمفعولية

```python
# Example: كَتَبَ زيدٌ الدَّرسَ
# زيدٌ: nominative → NominativeResolver → فاعل → agent_of(كتب)
# الدَّرسَ: accusative → AccusativeResolver → مفعول به → patient_of(كتب)
```

لكن: ليس كل مرفوع فاعلاً:
- `إنَّ زيدًا قائمٌ` → قائمٌ مرفوع لكنه خبر إن
- `كانَ زيدٌ عالمًا` → زيدٌ مرفوع لكنه اسم كان

لذلك `NominativeResolver` يستخدم: `irab_case + governing_factor_type + position` لتحديد الدور.

---

## 7. كيف يختلف يقين الإعراب عن يقين الواقع

```
syntactic_certainty ≠ factual_certainty
```

| المستوى | التعريف | مثال |
|---------|---------|------|
| `syntactic_certainty` | مدى وضوح الموقع النحوي | إنَّ زيدًا → اسم إن (واضح نحوياً) |
| `factual_certainty` | مدى ثبوت مضمون الجملة في الواقع | إنَّ زيدًا قائمٌ → لا يثبت قيامه بمجرد إن |

`MurabCertaintyPolicy` تُفرق بين المستويين:
- `evidence_effect = "syntactic_only"` → الإعراب لا يُثبت الواقع
- `evidence_effect = "none"` → التوكيد النحوي لا يزيد اليقين المعرفي

---

## 8. كيف يتكامل المعرب مع المبني

المبنيات تتحكم في **هيكل الحكم**. المعربات تكشف **مواقع الكلمات**.

```
إنَّ زيدًا قائمٌ

Mabni (إنَّ):
  type: nasikh
  function: توكيد / ربط
  evidence_effect: لا تُثبت الواقع

Murab (زيدًا):
  irab_case: accusative
  syntactic_role: اسم إن
  semantic_role: subject

Murab (قائمٌ):
  irab_case: nominative
  syntactic_role: خبر إن
  semantic_role: predicate

Graph:
  زيد --subject_of--> قيام
  قيام --predicated_by--> إنَّ
  certainty: syntactic_only (إن لا تثبت الواقع)
```

---

## 9. كيف يتكامل مع الجذر والوزن

```
كاتبٌ ماهرٌ

Morphosemantics (كاتب):
  root: ك-ت-ب (writing)
  pattern: فاعل → agent_pattern
  folds_agency: 0.9

Murab (كاتبٌ):
  irab_case: nominative
  syntactic_role: مبتدأ
  semantic_role: subject

Murab (ماهرٌ):
  irab_case: nominative
  syntactic_role: خبر
  semantic_role: predicate

Graph:
  كاتب --subject_of--> predication
  ماهر --predicate_of--> كاتب
  ماهر --modifies--> كاتب (property edge)
  كاتب --folds_agency--> writing_event
```

---

## 10. كيف يدخل في graph معرفي traceable

كل وحدة معربة (`MurabUnit`) مرتبطة بـ:

```
UnicodeChar → Grapheme → Token → MurabUnit
                                    ↓
                               IrabCase
                                    ↓
                           GoverningFactor
                                    ↓
                            SyntacticRole
                                    ↓
                             SemanticRole
                                    ↓
                            CognitiveGraph
                                    ↓
                            JudgmentTrace
```

`MurabTraceLinker` يربط كل وحدة بنطاق الأحرف في النص الأصلي:
```python
link = linker.link(unit, token_id="tok-001", char_start=0, char_end=5)
# link.unit_id, link.token_id, link.char_range, link.estimated
```

العلامة المقدرة تُذكر سببها:
```python
link = linker.link_estimated(unit, reason="تعذر - الاسم المقصور")
# link.estimated = True, link.reason = "تعذر..."
```

---

## Graph Builder Output

```python
analyzer = MurabAnalyzer()
units = analyzer.analyze("كَتَبَ زيدٌ الدَّرسَ بِالقَلَمِ")

builder = MurabGraphBuilder()
graph = builder.build(units, "كَتَبَ زيدٌ الدَّرسَ بِالقَلَمِ")

# graph.nodes: MurabUnitNode, IrabCaseNode, MarkerNode, ...
# graph.edges: agent_of, patient_of, governed_by, has_marker, ...
```

---

## CLI Commands

```bash
python -m mcd.cli murab-analyze --text "كتب زيد الدرس بالقلم" --output json
python -m mcd.cli irab-resolve --text "إن زيدًا قائمٌ" --output markdown
python -m mcd.cli murab-graph --text "جاء زيدٌ راكبًا" --output json
python -m mcd.cli irab-certainty --text "جاء الفتى" --output json
python -m mcd.cli murab-trace --text "كتب زيدٌ الدرسَ" --output markdown
```
