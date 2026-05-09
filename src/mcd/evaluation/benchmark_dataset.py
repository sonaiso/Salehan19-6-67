"""Benchmark Dataset — 10 curated Arabic examples for evaluation."""
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
    """Return the 10 canonical benchmark examples."""
    return [
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
    ]
