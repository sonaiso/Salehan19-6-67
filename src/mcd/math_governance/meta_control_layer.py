from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

from mcd.core.public_judgment import collapse_to_public_judgment


PATH_ZERO_IN_PATH = "zero_in_path"
PATH_HYPOTHESIS = "hypothesis"
PATH_LIKELY = "likely"
PATH_STRONG = "strong"
PATH_CERTIFICATE = "certificate"

PATH_STATUSES = {
    PATH_ZERO_IN_PATH,
    "possibility",
    PATH_HYPOTHESIS,
    PATH_LIKELY,
    PATH_STRONG,
    PATH_CERTIFICATE,
}

ROLE_CATEGORIES = {
    "phonetic",
    "syllabic",
    "root",
    "augment",
    "template",
    "inflectional",
    "building",
    "pronoun",
    "tool",
    "derivational",
    "semantic",
    "residual",
}

SUPPORT_RANK_NORMALIZATION_FACTOR = 10.0
CERTIFICATE_RANK_THRESHOLD = 0.95
STRONG_RANK_THRESHOLD = 0.75
LIKELY_RANK_THRESHOLD = 0.55


@dataclass
class MetaUnit:
    raw_unit: str
    position: int
    previous: str = ""
    next: str = ""
    layer: str = ""
    candidate_role: str = "residual"
    pattern: str = ""
    meta_pattern: str = ""
    constraints: dict[str, str] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    rank: float = 0.0
    residuals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_unit": self.raw_unit,
            "position": self.position,
            "previous": self.previous,
            "next": self.next,
            "layer": self.layer,
            "candidate_role": self.candidate_role,
            "pattern": self.pattern,
            "meta_pattern": self.meta_pattern,
            "constraints": self.constraints,
            "evidence": self.evidence,
            "rank": self.rank,
            "residuals": self.residuals,
        }


@dataclass
class CandidatePath:
    path_id: str
    units: list[MetaUnit]
    roles: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)
    constraints_passed: list[str] = field(default_factory=list)
    constraints_failed: list[str] = field(default_factory=list)
    evidence_chain: list[str] = field(default_factory=list)
    score: float = 0.0
    residuals: list[str] = field(default_factory=list)
    rank_components: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "units": [u.to_dict() for u in self.units],
            "roles": self.roles,
            "transformations": self.transformations,
            "constraints_passed": self.constraints_passed,
            "constraints_failed": self.constraints_failed,
            "evidence_chain": self.evidence_chain,
            "score": self.score,
            "residuals": self.residuals,
            "rank_components": self.rank_components,
        }


@dataclass
class PathAssessment:
    path_id: str
    impossible: bool
    path_status: str
    gate_rank: float
    support_rank: float
    final_rank: float
    residuals: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "impossible": self.impossible,
            "path_status": self.path_status,
            "gate_rank": self.gate_rank,
            "support_rank": self.support_rank,
            "final_rank": self.final_rank,
            "residuals": self.residuals,
            "reasons": self.reasons,
        }


@dataclass
class MetaCapsule:
    input: str
    selected_path: CandidatePath | None
    top_k_paths: list[CandidatePath]
    rejected_paths: list[CandidatePath]
    path_assessments: list[PathAssessment]
    unit_roles: dict[str, str]
    transformations: list[str]
    constraints: dict[str, list[str]]
    evidence: list[str]
    rank: float
    judgment: str
    residuals: list[str]
    trace: list[str]
    fold_hash: str
    unfold_recipe: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input,
            "selected_path": self.selected_path.to_dict() if self.selected_path else None,
            "top_k_paths": [p.to_dict() for p in self.top_k_paths],
            "rejected_paths": [p.to_dict() for p in self.rejected_paths],
            "path_assessments": [p.to_dict() for p in self.path_assessments],
            "unit_roles": self.unit_roles,
            "transformations": self.transformations,
            "constraints": self.constraints,
            "evidence": self.evidence,
            "rank": self.rank,
            "judgment": self.judgment,
            "residuals": self.residuals,
            "trace": self.trace,
            "fold_hash": self.fold_hash,
            "unfold_recipe": self.unfold_recipe,
        }


class MetaControlLayer:
    """Governs analysis paths instead of assigning absolute unit meaning."""

    def role(self, unit: MetaUnit, *, path: CandidatePath, context: dict[str, Any] | None = None) -> str:
        context = context or {}
        if unit.candidate_role in ROLE_CATEGORIES:
            return unit.candidate_role

        if unit.raw_unit == "ا" and context.get("alif_role") in {
            "long_vowel",
            "root",
            "augment",
            "dual_alif",
            "feminine_alif",
            "hamza_support",
            "tool_part",
        }:
            mapping = {
                "long_vowel": "phonetic",
                "root": "root",
                "augment": "augment",
                "dual_alif": "inflectional",
                "feminine_alif": "derivational",
                "hamza_support": "tool",
                "tool_part": "tool",
            }
            return mapping[context["alif_role"]]

        if unit.raw_unit == "م" and self.is_augment("م", pattern=unit.pattern, path=path, context=context):
            return "augment"

        return "residual"

    @staticmethod
    def is_augment(letter: str, *, pattern: str = "", path: CandidatePath | None = None, context: dict[str, Any] | None = None) -> bool:
        context = context or {}
        if not path:
            return False
        if letter != "م":
            return bool(context.get("explicit_augment", False))
        return pattern in {"مفعول", "مُفَعَّل", "مَفْعَل"}

    @staticmethod
    def haraka_role(*, is_mabni: bool, has_governing_factor: bool, syntactic_slot_requires_case: bool, attested_fixed_form: bool = False) -> dict[str, Any]:
        inflection_role = "none"
        building_role = "building" if is_mabni else "none"

        if not is_mabni and has_governing_factor and syntactic_slot_requires_case:
            inflection_role = "inflectional"
        elif not is_mabni and attested_fixed_form:
            inflection_role = "template"

        residuals = []
        if is_mabni and has_governing_factor:
            residuals.append("mabni_has_position_not_surface_case")

        return {
            "phonetic_role": "phonetic",
            "syllabic_role": "syllabic",
            "template_role": "template" if attested_fixed_form else "none",
            "inflection_role": inflection_role,
            "building_role": building_role,
            "semantic_trace": "position_sensitive",
            "residuals": residuals,
        }

    @staticmethod
    def pattern_status(*, is_productive: bool, is_analogical: bool, is_attested: bool, is_frozen: bool, is_irregular: bool) -> str:
        if is_irregular:
            return "irregular"
        if is_frozen:
            return "frozen"
        if is_productive:
            return "productive"
        if is_analogical:
            return "analogical"
        if is_attested:
            return "attested"
        return "doubtful"

    @staticmethod
    def inflection_mode(*, is_mabni: bool, has_i3rab_position: bool, has_estimated_case: bool, is_restricted_declinable: bool) -> str:
        if is_mabni and has_i3rab_position:
            return "mabni_with_i3rab_position"
        if is_mabni:
            return "mabni"
        if has_estimated_case:
            return "mu3rab_with_estimated_case"
        if is_restricted_declinable:
            return "indeclinable_by_restriction"
        return "mu3rab"

    @staticmethod
    def derivation_mode(*, historically_derived: bool, operationally_productive: bool, borrowed: bool, frozen_tool: bool) -> str:
        if borrowed:
            return "borrowed"
        if frozen_tool:
            return "frozen_tool"
        if historically_derived and not operationally_productive:
            return "lexicalized_derivative"
        if operationally_productive:
            return "mushtaqq"
        if historically_derived:
            return "doubtful"
        return "jamid"

    def impossible(self, path: CandidatePath) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        # explicit blocking constraints
        for failure in path.constraints_failed:
            lowered = failure.lower()
            if lowered.startswith("blocking:") or lowered.startswith("defeating:"):
                reasons.append(failure)

        # same-layer contradictory roles in same position without bridge
        by_position_layer: dict[tuple[int, str], set[str]] = {}
        for unit in path.units:
            key = (unit.position, unit.layer)
            by_position_layer.setdefault(key, set()).add(unit.candidate_role)
        for key, roles in by_position_layer.items():
            if "inflectional" in roles and "building" in roles and "bridge:layered" not in path.constraints_passed:
                reasons.append(f"conflict_at_{key[0]}_{key[1]}: inflectional_and_building_without_bridge")

        # contradictory absolute claims for single unit
        for unit in path.units:
            if unit.constraints.get("root_and_augment") == "same_axis_without_bridge":
                reasons.append(f"{unit.raw_unit}@{unit.position}: root_and_augment_same_axis")

        return len(reasons) > 0, reasons

    @staticmethod
    def _gate_rank(path: CandidatePath) -> float:
        components = path.rank_components or {}
        expected = [
            components.get("phonetic", 0.0),
            components.get("morphological", 0.0),
            components.get("syntactic", 0.0),
            components.get("semantic", 0.0),
            components.get("context", 0.0),
            components.get("evidence", 0.0),
        ]
        bounded = [max(0.0, min(1.0, v)) for v in expected]
        return min(bounded) if bounded else 0.0

    @staticmethod
    def _support_rank(path: CandidatePath) -> float:
        independent = len(set(path.evidence_chain))
        by_units = sum(len(set(unit.evidence)) for unit in path.units)
        raw = (independent + by_units) / SUPPORT_RANK_NORMALIZATION_FACTOR
        return max(0.0, min(1.0, round(raw, 4)))

    def assess(self, path: CandidatePath) -> PathAssessment:
        is_impossible, impossible_reasons = self.impossible(path)
        gate_rank = self._gate_rank(path)
        support_rank = self._support_rank(path)
        final_rank = min(gate_rank, support_rank)

        reasons = list(impossible_reasons)
        residuals = list(dict.fromkeys(path.residuals + [r for u in path.units for r in u.residuals]))

        if is_impossible:
            status = PATH_ZERO_IN_PATH
        elif final_rank >= CERTIFICATE_RANK_THRESHOLD and not any(r.startswith(("blocking", "defeating")) for r in residuals):
            status = PATH_CERTIFICATE
        elif final_rank >= STRONG_RANK_THRESHOLD:
            status = PATH_STRONG
        elif final_rank >= LIKELY_RANK_THRESHOLD:
            status = PATH_LIKELY
        elif final_rank > 0.0:
            status = PATH_HYPOTHESIS
        else:
            status = "possibility"

        if status not in PATH_STATUSES:
            status = PATH_HYPOTHESIS

        return PathAssessment(
            path_id=path.path_id,
            impossible=is_impossible,
            path_status=status,
            gate_rank=round(gate_rank, 4),
            support_rank=round(support_rank, 4),
            final_rank=round(final_rank, 4),
            residuals=residuals,
            reasons=reasons,
        )

    def govern(self, *, input_text: str, candidate_paths: list[CandidatePath], top_k: int = 3) -> MetaCapsule:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        assessed = [self.assess(path) for path in candidate_paths]
        assessed_by_id = {a.path_id: a for a in assessed}

        valid_paths = [p for p in candidate_paths if not assessed_by_id[p.path_id].impossible]
        rejected_paths = [p for p in candidate_paths if assessed_by_id[p.path_id].impossible]

        ranked = sorted(
            valid_paths,
            key=lambda p: (
                assessed_by_id[p.path_id].final_rank,
                p.score,
                len(set(p.evidence_chain)),
            ),
            reverse=True,
        )
        top_paths = ranked[:top_k]
        selected = top_paths[0] if top_paths else None

        selected_assessment = assessed_by_id[selected.path_id] if selected else None
        selected_status = selected_assessment.path_status if selected_assessment else PATH_ZERO_IN_PATH

        if selected_status == PATH_CERTIFICATE:
            judgment_source = "certificate"
        elif selected_status == PATH_ZERO_IN_PATH:
            judgment_source = "zero"
        else:
            judgment_source = "hypothesis"
        judgment = collapse_to_public_judgment(judgment_source)

        unit_roles: dict[str, str] = {}
        transformations: list[str] = []
        evidence: list[str] = []
        constraints = {"passed": [], "failed": []}
        residuals: list[str] = []
        trace: list[str] = []

        if selected:
            for unit in selected.units:
                key = f"{unit.raw_unit}@{unit.position}:{unit.layer or 'unknown'}"
                unit_roles[key] = self.role(unit, path=selected)
                evidence.extend(unit.evidence)
                residuals.extend(unit.residuals)
            transformations = selected.transformations
            constraints["passed"] = selected.constraints_passed
            constraints["failed"] = selected.constraints_failed
            evidence.extend(selected.evidence_chain)
            residuals.extend(selected.residuals)
            trace = [f"selected_path:{selected.path_id}"] + [f"transform:{t}" for t in selected.transformations]

        # preserve unresolved competing paths as residual truth memory
        if len(top_paths) > 1:
            residuals.append("competing_path")
            for p in top_paths[1:]:
                residuals.append(f"competing_path:{p.path_id}")
        for p in rejected_paths:
            residuals.append(f"rejected_path:{p.path_id}")

        residuals = list(dict.fromkeys(residuals))
        evidence = list(dict.fromkeys(evidence))

        payload_for_hash = {
            "input": input_text,
            "selected_path": selected.to_dict() if selected else None,
            "judgment": judgment,
            "rank": selected_assessment.final_rank if selected_assessment else 0.0,
            "residuals": residuals,
        }
        fold_hash = sha256(json.dumps(payload_for_hash, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

        unfold_recipe = {
            "algorithm": "MetaControl(input)=Fold(PreserveResiduals(KeepTopK(RankLikely(FilterImpossible(GenerateCandidatePaths(input))))))",
            "selected_path_id": selected.path_id if selected else None,
            "path_status": selected_status,
            "replay_steps": [
                "GenerateCandidates",
                "AttachRoles",
                "ApplyConstraints",
                "FilterImpossible",
                "RankLikely",
                "KeepTopK",
                "PreserveResiduals",
                "Fold",
                "Unfold",
            ],
        }

        return MetaCapsule(
            input=input_text,
            selected_path=selected,
            top_k_paths=top_paths,
            rejected_paths=rejected_paths,
            path_assessments=assessed,
            unit_roles=unit_roles,
            transformations=transformations,
            constraints=constraints,
            evidence=evidence,
            rank=selected_assessment.final_rank if selected_assessment else 0.0,
            judgment=judgment,
            residuals=residuals,
            trace=trace,
            fold_hash=fold_hash,
            unfold_recipe=unfold_recipe,
        )

    @staticmethod
    def unfold(capsule: MetaCapsule) -> dict[str, Any]:
        return {
            "selected_path": capsule.selected_path.to_dict() if capsule.selected_path else None,
            "path_assessments": [a.to_dict() for a in capsule.path_assessments],
            "trace": capsule.trace,
            "constraints": capsule.constraints,
            "evidence": capsule.evidence,
            "residuals": capsule.residuals,
            "fold_hash": capsule.fold_hash,
            "unfold_recipe": capsule.unfold_recipe,
        }
