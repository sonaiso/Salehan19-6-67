"""Dynamic Dataset Generator — generates BenchmarkExample from templates."""
from __future__ import annotations
import json
import random
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample

DEFAULT_TEMPLATES_PATH = Path(__file__).parent.parent.parent.parent / "data" / "evaluation" / "dynamic_templates_ar.json"


class DynamicDatasetGenerator:
    def __init__(self, seed: int = 42, templates_path: Path = DEFAULT_TEMPLATES_PATH):
        self.seed = seed
        self.rng = random.Random(seed)
        with open(templates_path, encoding="utf-8") as f:
            self.templates = json.load(f)["templates"]

    def _expand_template(self, tmpl: dict, idx: int) -> BenchmarkExample:
        text = tmpl["template"]
        variables = tmpl.get("variables", {})
        resolved = {}
        for var, values in variables.items():
            resolved[var] = values[idx % len(values)]
        for var, val in resolved.items():
            text = text.replace(f"{{{var}}}", val)

        tid = tmpl["template_id"].replace("TMPL-", "DYN-").replace("-001", "")
        example_id = f"{tid}-{idx+1:04d}"

        exp = tmpl.get("expected", {})
        certainty_policy = exp.get("certainty_policy", "suspend")
        judgment_types = exp.get("judgment_types", {})
        evidence_needs = exp.get("evidence_needs", {})
        required_separations = exp.get("required_separations", [])
        required_warnings = exp.get("required_warnings", [])

        if certainty_policy == "suspend":
            epistemic_status = "suspended"
        elif certainty_policy in ("near_certainty", "strong_knowledge"):
            epistemic_status = "verified"
        else:
            epistemic_status = "probable"

        if "ambiguous" in judgment_types:
            epistemic_status = "requires_context"

        tags = list(judgment_types.keys()) + [tmpl["template_id"].split("-")[1].lower()]
        tags = list(dict.fromkeys(tags))

        difficulty = "medium"
        if "adversarial" in tmpl["template_id"].lower():
            difficulty = "adversarial"

        return BenchmarkExample(
            example_id=example_id,
            input_text=text,
            language="ar",
            source_type="dynamic_generated",
            expected_judgment_types=judgment_types,
            expected_evidence_needs=evidence_needs,
            expected_certainty_policy=certainty_policy,
            expected_epistemic_status=epistemic_status,
            required_separations=required_separations,
            required_warnings=required_warnings,
            tags=tags,
            difficulty=difficulty,
            metadata={"template_id": tmpl["template_id"], "resolved": resolved},
        )

    def generate_from_templates(self, templates: list[dict], max_examples: int) -> list[BenchmarkExample]:
        examples = []
        per_template = max(1, max_examples // len(templates)) if templates else 0
        for tmpl in templates:
            variables = tmpl.get("variables", {})
            if variables:
                max_combos = max(len(v) for v in variables.values())
            else:
                max_combos = 1
            count = min(per_template, max_combos)
            for i in range(count):
                examples.append(self._expand_template(tmpl, i))
                if len(examples) >= max_examples:
                    break
            if len(examples) >= max_examples:
                break
        return examples

    def generate_profile(self, profile_name: str, count: int) -> list[BenchmarkExample]:
        return self.generate_from_templates(self.templates, count)

    def generate_balanced(self, count_per_category: int) -> list[BenchmarkExample]:
        examples = []
        for tmpl in self.templates:
            variables = tmpl.get("variables", {})
            if variables:
                max_combos = max(len(v) for v in variables.values())
            else:
                max_combos = 1
            count = min(count_per_category, max_combos)
            for i in range(count):
                examples.append(self._expand_template(tmpl, i))
        return examples

    def generate_adversarial(self, count: int) -> list[BenchmarkExample]:
        adv_templates = [t for t in self.templates if "ADV" in t["template_id"] or "ADVERSARIAL" in t["template_id"]]
        if not adv_templates:
            adv_templates = self.templates[:3]
        return self.generate_from_templates(adv_templates, count)
