"""Adversarial examples — utilities for loading and generating adversarial examples."""
from __future__ import annotations
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample

DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "evaluation"


def load_adversarial_examples(data_dir: Path = DEFAULT_DATA_DIR) -> list[BenchmarkExample]:
    from mcd.evaluation.dataset_loader import load_adversarial
    return load_adversarial(data_dir)


def generate_false_certainty_traps(count: int = 10) -> list[BenchmarkExample]:
    templates = [
        "من المؤكد أن {topic} حرام",
        "لا شك أن {topic} جائز",
        "يقيناً أن {topic} واجب",
    ]
    topics = ["الربا", "التأمين", "الموسيقى", "التصوير", "الاحتفال بالأعياد",
              "الغناء", "المصافحة", "التلفزيون", "الإنترنت", "الرياضة"]
    examples = []
    for i, topic in enumerate(topics[:count]):
        tmpl = templates[i % len(templates)]
        text = tmpl.replace("{topic}", topic)
        examples.append(BenchmarkExample(
            example_id=f"ADV-FC-{i+1:04d}",
            input_text=text,
            source_type="adversarial",
            expected_certainty_policy="suspend",
            expected_epistemic_status="suspended",
            expected_judgment_types={"shari": 0.9},
            required_warnings=["shari_evidence_required", "false_certainty_detected"],
            tags=["adversarial", "shari", "false_certainty"],
            difficulty="adversarial",
        ))
    return examples


def generate_harm_haram_conflations(count: int = 10) -> list[BenchmarkExample]:
    examples = []
    conflations = [
        "هذا الشيء ضار إذن هو حرام",
        "ما يضر البدن فهو حرام شرعاً",
        "الضرر دليل على التحريم",
        "كل شيء ضار محرم في الإسلام",
        "الأذى الجسدي يستلزم التحريم",
        "ما أضر فهو ممنوع دينياً",
        "الضار بالصحة حرام بالضرورة",
        "الإضرار بالنفس حرام شرعي",
        "الضرر النفسي يعني التحريم",
        "كل مضر فهو حرام",
    ]
    for i, text in enumerate(conflations[:count]):
        examples.append(BenchmarkExample(
            example_id=f"ADV-HH-{i+1:04d}",
            input_text=text,
            source_type="adversarial",
            expected_certainty_policy="suspend",
            expected_epistemic_status="suspended",
            expected_judgment_types={"shari": 0.7, "value": 0.3},
            required_warnings=["shari_evidence_required"],
            required_separations=["harm_vs_haram"],
            tags=["adversarial", "harm_vs_haram"],
            difficulty="adversarial",
        ))
    return examples
