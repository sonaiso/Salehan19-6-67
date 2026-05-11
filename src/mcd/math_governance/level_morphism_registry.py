from __future__ import annotations

from dataclasses import dataclass, field


_PRESERVE_KEYS = [
    "unit_identity",
    "trace",
    "relation",
    "evidence_need",
    "certainty_cap",
    "residual",
    "proof_blockers",
]


@dataclass
class LevelMorphism:
    morphism_id: str
    source_level: str
    target_level: str
    source_unit_types: list[str] = field(default_factory=list)
    target_unit_types: list[str] = field(default_factory=list)
    preserves: dict[str, bool] = field(default_factory=lambda: {k: True for k in _PRESERVE_KEYS})
    allowed_loss: list[str] = field(default_factory=list)
    forbidden_effects: list[str] = field(
        default_factory=lambda: [
            "create_evidence",
            "raise_epistemic_certainty_without_evidence",
            "issue_certificate",
            "erase_residual",
        ]
    )
    validation_rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "morphism_id": self.morphism_id,
            "source_level": self.source_level,
            "target_level": self.target_level,
            "source_unit_types": self.source_unit_types,
            "target_unit_types": self.target_unit_types,
            "preserves": self.preserves,
            "allowed_loss": self.allowed_loss,
            "forbidden_effects": self.forbidden_effects,
            "validation_rules": self.validation_rules,
        }


_DEFAULT_MORPHISMS: list[tuple[str, str, str]] = [
    ("raw_text_to_unicode", "raw_text", "unicode"),
    ("unicode_to_grapheme", "unicode", "grapheme"),
    ("grapheme_to_orthographic_unit", "grapheme", "orthographic_unit"),
    ("orthographic_unit_to_token", "orthographic_unit", "token"),
    ("token_to_lexeme", "token", "lexeme"),
    ("lexeme_to_morphology", "lexeme", "morphology"),
    ("morphology_to_phrase", "morphology", "phrase"),
    ("phrase_to_clause", "phrase", "clause"),
    ("clause_to_sentence", "clause", "sentence"),
    ("sentence_to_paragraph", "sentence", "paragraph"),
    ("paragraph_to_section", "paragraph", "section"),
    ("section_to_full_text", "section", "full_text"),
    ("full_text_to_discourse_graph", "full_text", "discourse_graph"),
    ("discourse_graph_to_claim_graph", "discourse_graph", "claim_graph"),
    ("claim_graph_to_proof_object", "claim_graph", "proof_object"),
    ("proof_object_to_final_judgment", "proof_object", "final_judgment"),
]


class LevelMorphismRegistry:
    def __init__(self) -> None:
        self._morphisms: dict[str, LevelMorphism] = {
            mid: LevelMorphism(
                morphism_id=mid,
                source_level=src,
                target_level=tgt,
                source_unit_types=[src, "unit"],
                target_unit_types=[tgt, "unit"],
                validation_rules=["trace_required", "no_evidence_creation", "no_certificate_issuance"],
            )
            for mid, src, tgt in _DEFAULT_MORPHISMS
        }

    def register(self, morphism: LevelMorphism) -> None:
        self._morphisms[morphism.morphism_id] = morphism

    def get(self, morphism_id: str) -> LevelMorphism | None:
        return self._morphisms.get(morphism_id)

    def find(self, source_level: str, target_level: str) -> LevelMorphism | None:
        for morphism in self._morphisms.values():
            if morphism.source_level == source_level and morphism.target_level == target_level:
                return morphism
        return None

    def get_all(self) -> list[LevelMorphism]:
        return list(self._morphisms.values())

    def validate_transition(self, source_level: str, target_level: str) -> tuple[bool, list[str]]:
        m = self.find(source_level, target_level)
        if m is None:
            return False, [f"No morphism registered for {source_level} -> {target_level}"]
        violations = []
        if not m.preserves.get("trace", False):
            violations.append(f"{m.morphism_id}: trace must be preserved")
        if "create_evidence" not in m.forbidden_effects:
            violations.append(f"{m.morphism_id}: create_evidence must be forbidden")
        if "issue_certificate" not in m.forbidden_effects:
            violations.append(f"{m.morphism_id}: issue_certificate must be forbidden")
        return len(violations) == 0, violations

    def validate_effects(
        self,
        morphism_id: str,
        *,
        create_evidence: bool = False,
        raise_certainty_without_evidence: bool = False,
        issue_certificate: bool = False,
        erase_residual: bool = False,
    ) -> tuple[bool, list[str]]:
        m = self.get(morphism_id)
        if m is None:
            return False, [f"Unknown morphism: {morphism_id}"]
        violations = []
        if create_evidence:
            violations.append(f"{morphism_id}: morphism cannot create evidence")
        if raise_certainty_without_evidence:
            violations.append(f"{morphism_id}: cannot raise certainty without evidence")
        if issue_certificate:
            violations.append(f"{morphism_id}: morphism cannot issue certificate")
        if erase_residual:
            violations.append(f"{morphism_id}: morphism cannot erase residual")
        return len(violations) == 0, violations
