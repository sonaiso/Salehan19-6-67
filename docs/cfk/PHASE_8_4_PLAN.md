# CFK Algebraic Closure — Phase 8.4

> **Status:** Plan (not yet implemented)
> **Scope:** `src/mcd/cfk/` only — no parallel package.
> **Tracking:** This document replaces a tracking issue. Treat its checklist as the canonical work breakdown for Phase 8.4.

---

## 1. الهدف

تحويل **CFK** من *kernel تجميعي* (يجمع projections من الطبقات الموجودة) إلى **جبر معرفي مُبرهَن** (Algebraic Closure) عبر إغلاق رياضي داخل `src/mcd/cfk/` — **بدون** إنشاء حزمة موازية جديدة، تجنّبًا لتكرار الخطأ البنيوي الذي أنتج PR #44 و PR #41 المتيتمين.

> **قاعدة تنفيذية صارمة:** خطة واحدة، فرع واحد، PRs **متسلسلة** (لا متوازية). لا يُفتح PR للوحدة `n+1` قبل دمج الوحدة `n`.

---

## 2. السياق المعماري الحالي

Phase 8.4 يبني فوق ما هو موجود — لا يستبدله:

| الطبقة الموجودة | الموقع | الدور في 8.4 |
|---|---|---|
| CFK Core (Phase 8) | `src/mcd/cfk/` (12 modules) | المضيف لكل وحدات 8.4 |
| CFK Hardening (Phase 8.1) | `cfk_integration_contract.py`, `cross_layer_conservation.py`, `reverse_trace.py`, `proof_object.py` | الأساس الذي يبني عليه `formal_proofs/` |
| Concept Geometry (Phase 8.3) | `src/mcd/concept_geometry/` (`ConceptCenter`, `JamidEssence`, `MushtaqUnit`) | يُلفّ عبر `cfk_memory.py` (adapter) |
| Morphosemantics (Phase 7.3) | `src/mcd/morphosemantics/` (`ConceptCenter`, `FoldedWordGraph`) | يُلفّ عبر `cfk_memory.py` (adapter) |
| Foldable Learning (Phase 7.2) | `src/mcd/foldable_learning/` (`FoldSignatureRegistry`, `PatternMemory`) | الأساس الذي يبني عليه `cfk_residual_loop.py` |

**ثوابت لا تُمَس** (موروثة من الطبقات الموجودة، يجب أن تظل صحيحة بعد كل وحدة في 8.4):

- `can_create_evidence = False` على `JamidEssence`, `MushtaqUnit`, `ConceptCenter`, `KernelProjection` (immutable عبر `__post_init__` + `object.__setattr__`).
- `can_issue_certificate = False` على نفس الكيانات.
- `MurabCertaintyPolicy.evidence_effect = "syntactic_only"` دائمًا.
- `MabniOperator.creates_evidence = False` دائمًا.
- Certificate gate في `proof_object.py`: `evidence ∧ conservation ∧ reverse_trace.complete`.

---

## 3. نطاق العمل — 6 وحدات (Checklist)

كل وحدة = PR صغير مستقل، يُدمَج بالترتيب على نفس فرع `phase-8.4-cfk-algebraic-closure`.

- [ ] **1. `cfk_algebra.py` — Operator Algebra**
  - تعريف العمليات كـ first-class objects: `compose`, `fold`, `unfold`, `refold`, `project`, `negate`, `condition`, `restrict`, `generalize`, `specialize`, `evidence_attach`, `certainty_update`, `residual_extract`.
  - قوانين قابلة للاختبار: Associativity, Identity, Idempotence (where applicable), Trace Preservation, Evidence Monotonicity, **No Certificate Creation**.
  - الموقع: `src/mcd/cfk/cfk_algebra.py` + `tests/test_cfk_algebra.py`.
  - CLI: `cfk-algebra-laws` (يعرض القوانين ونتائج فحصها).

- [ ] **2. `cfk_morphisms.py` — Level Morphism Registry (subset)**
  - 6 morphisms أساسية فقط: `RootPatternMorphism`, `SyntaxUnfoldingMorphism`, `GraphRefoldMorphism`, `ClaimToEvidenceMorphism`, `EvidenceToCertaintyMorphism`, `CertaintyToJudgmentMorphism`.
  - كل morphism يُثبِت: `preserves_nodes`, `preserves_edges`, `preserves_trace`, `preserves_certainty_constraints`, `preserves_evidence_constraints`, `does_not_create_certificate`, `does_not_convert_context_to_evidence`.
  - الموقع: `src/mcd/cfk/cfk_morphisms.py` + `tests/test_cfk_morphisms.py`.
  - CLI: `cfk-morphism-check`.

- [ ] **3. `cfk_jami_mani.py` — Jami/Mani Calculator**
  - `JamiScore = covered_positive_cases / total_positive_cases`
  - `ManiScore = excluded_negative_cases / total_negative_cases`
  - `ConceptTightness = harmonic_mean(JamiScore, ManiScore)`
  - Dataset أولي: 50 مفهومًا في `data/cfk/jami_mani_cases.json` مع `positive_cases` و `negative_cases`.
  - الموقع: `src/mcd/cfk/cfk_jami_mani.py` + `tests/test_cfk_jami_mani.py`.
  - CLI: `cfk-jami-mani --concept <id>`.

- [ ] **4. `cfk_memory.py` — Concept Memory Adapter**
  - **Adapter** فوق `concept_geometry.ConceptCenter` و `morphosemantics.ConceptCenter` الموجودين (لا rewrite، لا duplication).
  - فهرسة بـ `surface / root / pattern / domain`.
  - يربط `foldable_learning.PatternMemory` كذاكرة residual مشتركة على مستوى الـ kernel.
  - حقول: `allowed_relations`, `forbidden_relations`, `evidence_requirements`, `certainty_caps`, `known_residuals`, `examples`, `counterexamples`.
  - الموقع: `src/mcd/cfk/cfk_memory.py` + `tests/test_cfk_memory.py`.
  - CLI: `cfk-memory-lookup`.

- [ ] **5. `cfk_residual_loop.py` — GPT Residual → Curriculum Auto-Generation**
  - حلقة: `GPT proposal → CFU → Mathematical Contract → residual → classify → pattern → curriculum item → test`.
  - يبني فوق `foldable_learning/` الموجود (لا يُكرّره).
  - يولّد اختبارات تلقائية في `tests/generated/` من الـ residuals المتكررة (مع علامة `# auto-generated`).
  - الموقع: `src/mcd/cfk/cfk_residual_loop.py` + `tests/test_cfk_residual_loop.py`.
  - CLI: `cfk-residual-loop --proposals <path>`.

- [ ] **6. `formal_proofs/` — Formal Proof Sketches**
  - برهان رسمي عبر Python `hypothesis` (property-based) كحد أدنى — مع ملاحظات Lean 4 / Coq كأهداف لاحقة.
  - 3 نظريات على الأقل:
    - `evidence_monotonicity` — اليقين لا يزيد بلا دليل جديد.
    - `no_certificate_without_evidence` — `certificate ⇒ evidence ∧ conservation ∧ reverse_trace.complete`.
    - `trace_completeness_preservation` — كل morphism يحفظ `reverse_trace`.
  - الموقع: `formal_proofs/cfk/` + `docs/cfk/formal_proofs.md`.

---

## 4. معايير القبول (Acceptance Criteria — KPIs رياضية)

| # | KPI | المعنى | الهدف | يُقاس عبر |
|---|---|---|---:|---|
| 1 | Morphism Preservation Score | حفظ البنية عبر المورفيزمات | ≥ 0.97 | `tests/test_cfk_morphisms.py` |
| 2 | Operator Law Pass Rate | نجاح قوانين الجبر | ≥ 0.98 | property-based tests على ≥ 1000 حالة |
| 3 | Jami Score | تغطية المفهوم للحالات الموجبة | ≥ 0.90 | على dataset الـ 50 مفهومًا |
| 4 | Mani Score | استبعاد المفهوم للحالات السالبة | ≥ 0.90 | على dataset الـ 50 مفهومًا |
| 5 | Fold-Unfold Stability | `trace(fold(unfold(A))) ⊇ trace(A)` | ≥ 0.95 | property-based |
| 6 | Residual Compression Ratio | تحويل الأخطاء إلى أنماط قابلة لإعادة الاستخدام | ≥ 0.80 | عبر `cfk_residual_loop` |
| 7 | **Evidence Monotonicity** | اليقين لا يزيد بلا دليل | **1.00 (blocker)** | property-based + invariant check |
| 8 | Trace Completeness | كل حكم traceable من Unicode إلى الحكم النهائي | ≥ 0.99 | reverse_trace audit |
| 9 | ConceptCenter Recall | استرجاع المفهوم الصحيح من المدخل | ≥ 0.90 | على gold-set في `data/cfk/` |
| 10 | **False Certificate Rate** | شهادات خاطئة | **≤ 0.01 (blocker)** | adversarial test set |

**Blocker rule:** أي فشل في KPI #7 أو #10 يوقف الدمج فورًا — لا تنازل.

---

## 5. قواعد الدمج (Merge Discipline)

1. **Issue واحد، فرع واحد، PRs متسلسلة.** فرع العمل: `phase-8.4-cfk-algebraic-closure`.
2. كل وحدة تأتي مع: كود + اختبارات + تحديث `src/mcd/cli.py` + توثيق + KPI واحد على الأقل من الجدول أعلاه.
3. لا يُفتح PR للوحدة `n+1` قبل دمج الوحدة `n`.
4. KPIs #7 و #10 **blockers** — أي فشل فيهما يوقف الدمج.
5. لا تُنشأ حزمة جديدة بمستوى `src/mcd/cfk/` — كل شيء **داخل** `cfk/` (إضافة وحدات، لا استبدال).
6. كل PR يجب أن يُبقي اختبارات CFK الحالية (234 اختبار: 127 Phase 8 + 107 Phase 8.1) خضراء.
7. الثوابت في القسم 2 (`can_create_evidence=False`, `can_issue_certificate=False`, `evidence_effect="syntactic_only"`, certificate gate) **لا تُعدَّل** إلا بإجماع موثَّق.

---

## 6. اختبار التشغيل (Test Run Convention)

موروث من الطبقات الحالية، لا يتغير:

```bash
PYTHONPATH=src python -m pytest tests/test_cfk*.py -q
```

العدد المتوقع بعد كل وحدة:

| بعد إنجاز | عدد اختبارات CFK المتوقع |
|---|---:|
| Phase 8.1 (الحالي) | 234 |
| + الوحدة 1 (algebra) | ≥ 254 |
| + الوحدة 2 (morphisms) | ≥ 274 |
| + الوحدة 3 (jami_mani) | ≥ 289 |
| + الوحدة 4 (memory) | ≥ 304 |
| + الوحدة 5 (residual_loop) | ≥ 319 |
| + الوحدة 6 (formal_proofs) | ≥ 334 |

---

## 7. ما يُغلَق بهذه الخطة

- إغلاق رسمي للحالة الرياضية المفتوحة منذ PR #41 و PR #44 المتيتمَين.
- نقل المشروع من *post-hoc integration* إلى *mathematical unification* داخل CFK.
- جاهزية لإصدار **Cognitive Governance SDK** (Phase 9) **بعد** اكتمال هذه الوحدات الست — لا قبلها.

---

## 8. ما هو خارج النطاق (Out of Scope)

- لا تعديل على `concept_geometry/`, `morphosemantics/`, `foldable_learning/`, `mabni/`, `murab/`, `fractal_kernel/` — الوصول إليها يكون **read-only عبر adapters فقط**.
- لا تغيير في عقد `proof_object.py` certificate gate — يُبنى عليه فقط.
- لا حزمة `cfk_v2/` أو `cognitive_algebra/` موازية. التوسعة **داخل** `src/mcd/cfk/`.
