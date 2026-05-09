"""Benchmark Dataset — curated Arabic examples for evaluation.

Phase 1 dataset expansion: 50 examples covering all judgment categories:
  epistemic, technical, value, shari, practical,
  linguistic, ambiguous, analogy, metaphor, usuli_reasoning,
  civilization/civility distinction, harm-vs-haram, social-epistemic.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BenchmarkExample:
    example_id: str
    input_text: str
    task_type: str
    expected_behavior: dict
    notes: str = ""


def load_benchmark_examples() -> list[BenchmarkExample]:
    """Return the canonical benchmark examples."""
    return [
        # ─── Epistemic / physical ─────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-01",
            input_text="النار تحرق",
            task_type="epistemic_classification",
            expected_behavior={
                "judgment_type": "epistemic",
                "root_domain": "universe",
                "evidence_type": "sensory_experimental",
                "certainty_policy": ["strong_knowledge", "near_certainty"],
                "should_suspend": False,
            },
            notes="Empirical physical claim — should receive strong certainty.",
        ),
        # ─── Ambiguity detection ──────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-02",
            input_text="علم",
            task_type="ambiguity_detection",
            expected_behavior={
                "judgment_type": "ambiguous",
                "requires_context": True,
                "certainty_policy": ["suspend", "hypothesis"],
                "should_suspend": True,
            },
            notes="Single word — deeply ambiguous. System should request context.",
        ),
        # ─── Linguistic definition ────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-03",
            input_text="ما معنى علم؟",
            task_type="linguistic_definition",
            expected_behavior={
                "judgment_type": "linguistic",
                "evidence_type": "contextual_linguistic",
                "certainty_policy": ["suspend", "hypothesis"],
                "should_suspend": True,
            },
            notes="Polysemous word — multiple valid meanings. Requires disambiguation.",
        ),
        # ─── Epistemic value judgment (harm) ──────────────────────────────
        BenchmarkExample(
            example_id="BM-04",
            input_text="هل الكذب ضار؟",
            task_type="epistemic_value_judgment",
            expected_behavior={
                "judgment_type": ["epistemic", "value"],
                "not_shari": True,
                "evidence_type": "empirical_social",
                "certainty_policy": ["probable", "strong"],
                "should_suspend": False,
            },
            notes="Harm question — epistemic/empirical, not shari.",
        ),
        # ─── Shari judgment ───────────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-05",
            input_text="هل الكذب حرام؟",
            task_type="shari_judgment",
            expected_behavior={
                "judgment_type": "shari",
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
                "harm_haram_separation": True,
            },
            notes="Shari ruling — requires textual religious evidence. Should NOT conflate with harm.",
        ),
        # ─── Technical / practical ────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-06",
            input_text="كيف نبني API للديكودر؟",
            task_type="technical_practical",
            expected_behavior={
                "judgment_type": ["technical", "practical"],
                "root_domain": ["human", "life"],
                "evidence_type": "technical_textual",
                "no_shari": True,
                "certainty_policy": ["probable", "strong_knowledge"],
                "should_suspend": False,
            },
            notes="Technical construction question — no shari dimension.",
        ),
        # ─── Complex multi-domain ─────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-07",
            input_text="كيف نبني نظامًا تعليميًا عربيًا يستخدم الذكاء الاصطناعي لتربية العقل؟",
            task_type="complex_system_design",
            expected_behavior={
                "judgment_type": ["technical", "practical", "value"],
                "root_domain": ["human", "life"],
                "concept_types": ["system", "tool", "purpose"],
                "dimensions": ["technology", "culture", "method"],
                "certainty_policy": ["hypothesis", "probable"],
                "should_suspend": False,
            },
            notes="Complex multi-domain question — system + cultural + educational.",
        ),
        # ─── Analogy without illah ────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-08",
            input_text="هذا مثل ذاك إذن له نفس الحكم",
            task_type="analogy_detection",
            expected_behavior={
                "judgment_type": ["possible_analogy"],
                "missing_illah": True,
                "certainty_policy": ["suspend", "weak"],
                "should_suspend": True,
            },
            notes="Analogy without stated illah — should be flagged as weak reasoning.",
        ),
        # ─── Civilization vs civility ─────────────────────────────────────
        BenchmarkExample(
            example_id="BM-09",
            input_text="الذكاء الاصطناعي أداة مدنية أم مفهوم حضاري؟",
            task_type="civilization_distinction",
            expected_behavior={
                "judgment_type": ["value", "epistemic"],
                "distinction_required": "civilization_vs_civility",
                "not_purely_technical": True,
                "certainty_policy": ["hypothesis", "probable"],
                "should_suspend": False,
            },
            notes="Civilization/civility distinction — not purely technical question.",
        ),
        # ─── Social epistemic ─────────────────────────────────────────────
        BenchmarkExample(
            example_id="BM-10",
            input_text="المجتمع يرفض الفساد",
            task_type="social_epistemic",
            expected_behavior={
                "judgment_type": ["epistemic", "social"],
                "evidence_type": "social_empirical",
                "certainty_policy": ["hypothesis", "probable"],
                "requires_data": True,
                "high_certainty_unwarranted": True,
                "should_suspend": False,
            },
            notes="Social/public opinion claim — needs data, not high certainty without evidence.",
        ),

        # ─── Phase 1 expansion: Epistemic ────────────────────────────────
        BenchmarkExample(
            example_id="BM-11",
            input_text="الماء يغلي عند مئة درجة مئوية",
            task_type="epistemic_classification",
            expected_behavior={
                "judgment_type": "epistemic",
                "root_domain": "universe",
                "evidence_type": "experimental",
                "certainty_policy": ["near_certainty", "strong_knowledge"],
                "should_suspend": False,
            },
            notes="Scientific fact — high certainty from repeatable experiment.",
        ),
        BenchmarkExample(
            example_id="BM-12",
            input_text="هل الأرض كروية؟",
            task_type="epistemic_classification",
            expected_behavior={
                "judgment_type": "epistemic",
                "evidence_type": "sensory_experimental",
                "certainty_policy": ["near_certainty", "strong_knowledge"],
                "should_suspend": False,
            },
            notes="Established scientific claim.",
        ),
        BenchmarkExample(
            example_id="BM-13",
            input_text="ما هو الذكاء؟",
            task_type="epistemic_definition",
            expected_behavior={
                "judgment_type": ["epistemic", "value"],
                "certainty_policy": ["hypothesis", "probable"],
                "should_suspend": False,
            },
            notes="Contested epistemic definition — multiple frameworks exist.",
        ),

        # ─── Phase 1 expansion: Linguistic ───────────────────────────────
        BenchmarkExample(
            example_id="BM-14",
            input_text="ما دلالة كلمة 'قلب' في اللغة العربية؟",
            task_type="linguistic_definition",
            expected_behavior={
                "judgment_type": "linguistic",
                "evidence_type": "linguistic_textual",
                "certainty_policy": ["suspend", "hypothesis"],
                "should_suspend": True,
            },
            notes="Polysemous Arabic word — heart/mind/turning. Requires contextual disambiguation.",
        ),
        BenchmarkExample(
            example_id="BM-15",
            input_text="ما جذر كلمة 'استخرج'؟",
            task_type="linguistic_morphology",
            expected_behavior={
                "judgment_type": "linguistic",
                "evidence_type": "linguistic",
                "certainty_policy": ["strong_knowledge", "near_certainty"],
                "should_suspend": False,
            },
            notes="Morphological analysis — deterministic, high certainty.",
        ),
        BenchmarkExample(
            example_id="BM-16",
            input_text="ما معنى مصطلح 'الاجتهاد' في الفقه؟",
            task_type="linguistic_terminological",
            expected_behavior={
                "judgment_type": ["linguistic", "usuli_reasoning"],
                "evidence_type": "textual_linguistic",
                "certainty_policy": ["strong_knowledge", "hypothesis"],
                "should_suspend": False,
            },
            notes="Technical jurisprudential term — linguistic + usuli dimensions.",
        ),

        # ─── Phase 1 expansion: Ambiguous ────────────────────────────────
        BenchmarkExample(
            example_id="BM-17",
            input_text="هل هذا جائز؟",
            task_type="ambiguity_detection",
            expected_behavior={
                "judgment_type": "ambiguous",
                "requires_context": True,
                "certainty_policy": ["suspend"],
                "should_suspend": True,
            },
            notes="No referent — 'هذا' is undefined. System must suspend.",
        ),
        BenchmarkExample(
            example_id="BM-18",
            input_text="كيف نتعامل مع هذا؟",
            task_type="ambiguity_detection",
            expected_behavior={
                "judgment_type": "ambiguous",
                "requires_context": True,
                "certainty_policy": ["suspend"],
                "should_suspend": True,
            },
            notes="Missing referent — 'هذا' requires specification.",
        ),
        BenchmarkExample(
            example_id="BM-19",
            input_text="هل يصح؟",
            task_type="ambiguity_detection",
            expected_behavior={
                "judgment_type": "ambiguous",
                "requires_context": True,
                "certainty_policy": ["suspend"],
                "should_suspend": True,
            },
            notes="Completely decontextualised question.",
        ),

        # ─── Phase 1 expansion: Analogy ──────────────────────────────────
        BenchmarkExample(
            example_id="BM-20",
            input_text="الخمر حرام لأنه مسكر، وكل مسكر حرام",
            task_type="analogy_valid",
            expected_behavior={
                "judgment_type": ["shari", "analogy"],
                "illah_stated": True,
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "should_suspend": True,
            },
            notes="Analogy with explicit illah — properly structured, but still requires shari evidence.",
        ),
        BenchmarkExample(
            example_id="BM-21",
            input_text="هذا الأمر مثل الربا تمامًا إذن هو حرام",
            task_type="analogy_weak",
            expected_behavior={
                "judgment_type": ["analogy"],
                "missing_illah": True,
                "certainty_policy": ["suspend", "weak"],
                "should_suspend": True,
            },
            notes="Weak analogy without explicit illah linking the two cases.",
        ),
        BenchmarkExample(
            example_id="BM-22",
            input_text="الذكاء الاصطناعي مثل الطباعة، إذن يجب تنظيمه بنفس الطريقة",
            task_type="analogy_detection",
            expected_behavior={
                "judgment_type": ["analogy", "practical"],
                "certainty_policy": ["suspend", "hypothesis"],
                "should_suspend": True,
            },
            notes="Historical analogy — interesting but missing shared illah.",
        ),

        # ─── Phase 1 expansion: Metaphor ─────────────────────────────────
        BenchmarkExample(
            example_id="BM-23",
            input_text="العلم نور",
            task_type="metaphor_detection",
            expected_behavior={
                "judgment_type": ["metaphor", "value"],
                "certainty_policy": ["hypothesis", "probable"],
                "should_suspend": False,
            },
            notes="Figurative expression — not a literal physical claim.",
        ),
        BenchmarkExample(
            example_id="BM-24",
            input_text="الوقت كالسيف إن لم تقطعه قطعك",
            task_type="metaphor_detection",
            expected_behavior={
                "judgment_type": ["metaphor", "value"],
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Proverb / metaphor — non-literal, value-laden.",
        ),
        BenchmarkExample(
            example_id="BM-25",
            input_text="القلوب المريضة لا تقبل الحق",
            task_type="metaphor_detection",
            expected_behavior={
                "judgment_type": ["metaphor", "value"],
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Metaphorical hearts — figurative, not medical.",
        ),

        # ─── Phase 1 expansion: Usuli reasoning ──────────────────────────
        BenchmarkExample(
            example_id="BM-26",
            input_text="ما ضوابط الاجتهاد في المسائل المستجدة؟",
            task_type="usuli_reasoning",
            expected_behavior={
                "judgment_type": ["usuli_reasoning", "epistemic"],
                "evidence_type": "textual_shari",
                "certainty_policy": ["hypothesis", "strong_knowledge"],
                "should_suspend": False,
            },
            notes="Usul al-fiqh methodology question.",
        ),
        BenchmarkExample(
            example_id="BM-27",
            input_text="هل يُقاس هذا الحكم الجديد على القديم بجامع العلة؟",
            task_type="usuli_analogy",
            expected_behavior={
                "judgment_type": ["usuli_reasoning", "analogy", "shari"],
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend", "hypothesis"],
                "should_suspend": True,
            },
            notes="Usuli qiyas question — requires shari evidence for illah.",
        ),

        # ─── Phase 1 expansion: Value judgments ──────────────────────────
        BenchmarkExample(
            example_id="BM-28",
            input_text="هل الغش في الامتحانات ضار؟",
            task_type="epistemic_value_judgment",
            expected_behavior={
                "judgment_type": ["value", "epistemic"],
                "not_shari": True,
                "certainty_policy": ["strong_knowledge", "probable"],
                "should_suspend": False,
            },
            notes="Harm-based value judgment — no shari dimension needed.",
        ),
        BenchmarkExample(
            example_id="BM-29",
            input_text="هل التدخين ضار بالصحة؟",
            task_type="epistemic_value_judgment",
            expected_behavior={
                "judgment_type": ["value", "epistemic"],
                "root_domain": "universe",
                "evidence_type": "experimental",
                "certainty_policy": ["strong_knowledge", "near_certainty"],
                "should_suspend": False,
            },
            notes="Medical-empirical harm question — high certainty from scientific evidence.",
        ),
        BenchmarkExample(
            example_id="BM-30",
            input_text="هل التدخين حرام؟",
            task_type="shari_judgment",
            expected_behavior={
                "judgment_type": "shari",
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
                "harm_haram_separation": True,
            },
            notes="Shari ruling — different question from 'is it harmful'. Requires textual evidence.",
        ),

        # ─── Phase 1 expansion: Shari judgments ──────────────────────────
        BenchmarkExample(
            example_id="BM-31",
            input_text="هل الصلاة فريضة؟",
            task_type="shari_judgment",
            expected_behavior={
                "judgment_type": "shari",
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
            },
            notes="Clear shari obligation — requires Quran/Sunnah evidence.",
        ),
        BenchmarkExample(
            example_id="BM-32",
            input_text="هل الربا حرام؟",
            task_type="shari_judgment",
            expected_behavior={
                "judgment_type": "shari",
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
            },
            notes="Shari prohibition — textual evidence required.",
        ),

        # ─── Phase 1 expansion: Technical ────────────────────────────────
        BenchmarkExample(
            example_id="BM-33",
            input_text="كيف أكتب خوارزمية بحث ثنائي في Python؟",
            task_type="technical",
            expected_behavior={
                "judgment_type": ["technical", "practical"],
                "evidence_type": "technical",
                "certainty_policy": ["strong_knowledge", "near_certainty"],
                "should_suspend": False,
            },
            notes="Pure technical question — deterministic answer.",
        ),
        BenchmarkExample(
            example_id="BM-34",
            input_text="ما الفرق بين REST و GraphQL؟",
            task_type="technical",
            expected_behavior={
                "judgment_type": ["technical", "epistemic"],
                "evidence_type": "technical",
                "certainty_policy": ["strong_knowledge"],
                "should_suspend": False,
            },
            notes="Technical comparison — epistemic with technical evidence.",
        ),
        BenchmarkExample(
            example_id="BM-35",
            input_text="كيف نصمم نظام تخزين موزع؟",
            task_type="technical_practical",
            expected_behavior={
                "judgment_type": ["technical", "practical"],
                "certainty_policy": ["strong_knowledge", "hypothesis"],
                "should_suspend": False,
            },
            notes="Complex technical design — some uncertainty in trade-offs.",
        ),

        # ─── Phase 1 expansion: Practical ────────────────────────────────
        BenchmarkExample(
            example_id="BM-36",
            input_text="ما خطوات بناء مشروع بحثي ناجح؟",
            task_type="practical",
            expected_behavior={
                "judgment_type": ["practical", "epistemic"],
                "certainty_policy": ["strong_knowledge", "hypothesis"],
                "should_suspend": False,
            },
            notes="Practical planning question.",
        ),
        BenchmarkExample(
            example_id="BM-37",
            input_text="ماذا نفعل لتحسين جودة التعليم في العالم العربي؟",
            task_type="practical",
            expected_behavior={
                "judgment_type": ["practical", "value", "epistemic"],
                "root_domain": "life",
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Complex socio-practical question — wide scope, hypothesis level.",
        ),

        # ─── Phase 1 expansion: Harm vs Haram ────────────────────────────
        BenchmarkExample(
            example_id="BM-38",
            input_text="هل الغيبة ضارة؟",
            task_type="epistemic_value_judgment",
            expected_behavior={
                "judgment_type": ["value", "epistemic"],
                "not_shari": True,
                "certainty_policy": ["strong_knowledge", "probable"],
                "should_suspend": False,
            },
            notes="Social harm question — empirical, not shari.",
        ),
        BenchmarkExample(
            example_id="BM-39",
            input_text="هل الغيبة حرام؟",
            task_type="shari_judgment",
            expected_behavior={
                "judgment_type": "shari",
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
                "harm_haram_separation": True,
            },
            notes="Shari ruling on backbiting — separate from harm dimension.",
        ),
        BenchmarkExample(
            example_id="BM-40",
            input_text="هل الكحول ضار ومحرَّم في آنٍ واحد؟",
            task_type="harm_haram_dual",
            expected_behavior={
                "judgment_type": ["value", "shari", "epistemic"],
                "harm_haram_separation": True,
                "certainty_policy": ["suspend"],
                "should_suspend": True,
            },
            notes="Dual harm+haram question — both dimensions must be distinguished.",
        ),

        # ─── Phase 1 expansion: Civilization / Civility ──────────────────
        BenchmarkExample(
            example_id="BM-41",
            input_text="هل الإنترنت أداة مدنية أم ظاهرة حضارية؟",
            task_type="civilization_distinction",
            expected_behavior={
                "judgment_type": ["value", "epistemic"],
                "distinction_required": "civilization_vs_civility",
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Civilization vs civility distinction — Internet as tool or culture.",
        ),
        BenchmarkExample(
            example_id="BM-42",
            input_text="ما الفرق بين المدنية والحضارة؟",
            task_type="epistemic_conceptual",
            expected_behavior={
                "judgment_type": ["epistemic", "value"],
                "distinction_required": "civilization_vs_civility",
                "certainty_policy": ["strong_knowledge", "hypothesis"],
                "should_suspend": False,
            },
            notes="Conceptual distinction — core Nabhani framework concept.",
        ),

        # ─── Phase 1 expansion: Social epistemic ─────────────────────────
        BenchmarkExample(
            example_id="BM-43",
            input_text="الشباب العربي يرفض الفساد ويطالب بالإصلاح",
            task_type="social_epistemic",
            expected_behavior={
                "judgment_type": ["epistemic", "social"],
                "evidence_type": "social_empirical",
                "certainty_policy": ["hypothesis", "probable"],
                "requires_data": True,
                "should_suspend": False,
            },
            notes="Social claim — requires empirical data before high certainty.",
        ),
        BenchmarkExample(
            example_id="BM-44",
            input_text="الرأي العام يؤيد هذا القرار",
            task_type="social_epistemic",
            expected_behavior={
                "judgment_type": ["epistemic", "social"],
                "certainty_policy": ["hypothesis"],
                "requires_data": True,
                "high_certainty_unwarranted": True,
                "should_suspend": False,
            },
            notes="Public opinion claim — hypothesis without polling data.",
        ),

        # ─── Phase 1 expansion: Complex multi-dimension ──────────────────
        BenchmarkExample(
            example_id="BM-45",
            input_text="هل يجوز استخدام الذكاء الاصطناعي في اتخاذ القرارات القضائية؟",
            task_type="complex_shari_technical",
            expected_behavior={
                "judgment_type": ["shari", "technical", "value"],
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "should_suspend": True,
                "harm_haram_separation": True,
            },
            notes="Complex question with shari + technical dimensions.",
        ),
        BenchmarkExample(
            example_id="BM-46",
            input_text="ما حكم العمل في شركة تبيع منتجات محرمة وأخرى مباحة؟",
            task_type="shari_practical",
            expected_behavior={
                "judgment_type": ["shari", "practical"],
                "evidence_type": "shari_textual",
                "certainty_policy": ["suspend"],
                "requires_shari_evidence": True,
                "should_suspend": True,
            },
            notes="Mixed shari-practical scenario.",
        ),
        BenchmarkExample(
            example_id="BM-47",
            input_text="كيف نقيس نجاح نظام تعليمي؟",
            task_type="epistemic_practical",
            expected_behavior={
                "judgment_type": ["epistemic", "practical", "value"],
                "certainty_policy": ["hypothesis", "probable"],
                "should_suspend": False,
            },
            notes="Multi-dimensional measurement question.",
        ),
        BenchmarkExample(
            example_id="BM-48",
            input_text="هل الديمقراطية نظام حكم صحيح؟",
            task_type="epistemic_value",
            expected_behavior={
                "judgment_type": ["epistemic", "value"],
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Contested political philosophy question — hypothesis level.",
        ),
        BenchmarkExample(
            example_id="BM-49",
            input_text="ما دليل أن الله موجود؟",
            task_type="epistemic_theological",
            expected_behavior={
                "judgment_type": ["epistemic"],
                "certainty_policy": ["hypothesis", "suspend"],
                "should_suspend": True,
            },
            notes="Theological epistemic question — evidence type determines policy.",
        ),
        BenchmarkExample(
            example_id="BM-50",
            input_text="هل اليقين الكامل ممكن في المسائل الإنسانية؟",
            task_type="epistemic_philosophical",
            expected_behavior={
                "judgment_type": ["epistemic", "value"],
                "certainty_policy": ["hypothesis"],
                "should_suspend": False,
            },
            notes="Philosophical epistemic question — hypothesis is appropriate.",
        ),
    ]
