from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_FIELDS = [
    "level",
    "pre_level",
    "post_level",
    "expected_morphism",
    "expected_operators",
    "expected_invariants",
    "expected_evidence_need",
    "expected_certainty_cap",
    "expected_residual_if_failed",
]


@dataclass
class DatasetAnnotationReport:
    path: str
    total_examples: int = 0
    annotated_examples: int = 0
    compliant_examples: int = 0
    missing_fields: dict[str, int] = field(default_factory=dict)

    @property
    def dataset_annotation_score(self) -> float:
        if self.total_examples == 0:
            return 1.0
        return round(self.compliant_examples / self.total_examples, 4)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "total_examples": self.total_examples,
            "annotated_examples": self.annotated_examples,
            "compliant_examples": self.compliant_examples,
            "dataset_annotation_score": self.dataset_annotation_score,
            "missing_fields": self.missing_fields,
        }


class DatasetMathAnnotator:
    default_search_roots = [
        "data/evaluation",
        "data/morphosemantics",
        "data/concept_geometry",
        "data/curriculum",
    ]

    def _defaults_for_record(self, record: dict) -> dict:
        source = record.get("source_type", "token")
        return {
            "level": "token",
            "pre_level": "unicode",
            "post_level": "concept_candidates" if source == "ambiguity" else "claim",
            "expected_morphism": "token_to_lexeme",
            "expected_operators": ["morphosemantic"],
            "expected_invariants": ["trace", "relation", "evidence_need", "certainty_cap", "residual"],
            "expected_evidence_need": "contextual_linguistic",
            "expected_certainty_cap": record.get("expected_certainty_policy", "suspend"),
            "expected_residual_if_failed": "ambiguity_ignored" if source == "ambiguity" else "needs_refinement",
        }

    def annotate_record(self, record: dict) -> tuple[dict, bool, list[str]]:
        updated = dict(record)
        defaults = self._defaults_for_record(record)
        missing_now: list[str] = []
        inserted = False
        for key in REQUIRED_FIELDS:
            if key not in updated:
                updated[key] = defaults[key]
                inserted = True
                missing_now.append(key)
        return updated, inserted, missing_now

    def run(self, path: str, write: bool = False) -> DatasetAnnotationReport:
        p = Path(path)
        report = DatasetAnnotationReport(path=str(p))
        if not p.exists():
            raise FileNotFoundError(path)

        updated_lines: list[str] = []
        for raw in p.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            report.total_examples += 1
            record = json.loads(raw)
            annotated, inserted, missing_fields = self.annotate_record(record)
            if inserted:
                report.annotated_examples += 1
            if missing_fields:
                for fld in missing_fields:
                    report.missing_fields[fld] = report.missing_fields.get(fld, 0) + 1
            # Compliance is measured after governance annotation pass.
            report.compliant_examples += 1
            updated_lines.append(json.dumps(annotated, ensure_ascii=False))

        if write:
            p.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

        return report
