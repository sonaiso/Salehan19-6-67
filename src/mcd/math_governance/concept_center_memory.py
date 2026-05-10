from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConceptCenterRecord:
    concept_id: str
    surfaces: list[str] = field(default_factory=list)
    roots: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    allowed_relations: list[str] = field(default_factory=list)
    forbidden_relations: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    certainty_caps: list[str] = field(default_factory=list)
    known_residuals: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "concept_id": self.concept_id,
            "surfaces": self.surfaces,
            "roots": self.roots,
            "patterns": self.patterns,
            "domains": self.domains,
            "allowed_relations": self.allowed_relations,
            "forbidden_relations": self.forbidden_relations,
            "evidence_requirements": self.evidence_requirements,
            "certainty_caps": self.certainty_caps,
            "known_residuals": self.known_residuals,
            "examples": self.examples,
            "counterexamples": self.counterexamples,
            "trace_refs": self.trace_refs,
        }


class ConceptCenterMemory:
    def __init__(self) -> None:
        self._records: dict[str, ConceptCenterRecord] = {}

    def add_record(self, record: ConceptCenterRecord) -> None:
        self._records[record.concept_id] = record

    def search_by_surface(self, surface: str) -> list[ConceptCenterRecord]:
        return [r for r in self._records.values() if surface in r.surfaces]

    def search_by_root(self, root: str) -> list[ConceptCenterRecord]:
        return [r for r in self._records.values() if root in r.roots]

    def search_by_domain(self, domain: str) -> list[ConceptCenterRecord]:
        return [r for r in self._records.values() if domain in r.domains]

    def attach_residual(self, concept_id: str, residual: str) -> bool:
        rec = self._records.get(concept_id)
        if rec is None:
            return False
        if residual not in rec.known_residuals:
            rec.known_residuals.append(residual)
        return True

    def get_evidence_requirements(self, concept_id: str) -> list[str]:
        rec = self._records.get(concept_id)
        return rec.evidence_requirements if rec else []

    def export(self) -> list[dict]:
        return [r.to_dict() for r in self._records.values()]

    @staticmethod
    def can_certify_alone() -> bool:
        return False
