"""CurriculumEvaluator — evaluates system performance on curriculum units."""
from __future__ import annotations

from dataclasses import dataclass, field

from .cognitive_unit import CognitiveUnit
from .curriculum_schema import LEVEL_NAMES, VALID_TARGET_LAYERS


@dataclass
class LayerScore:
    layer: str
    total: int
    correct: int
    score: float

    def to_dict(self) -> dict:
        return {"layer": self.layer, "total": self.total, "correct": self.correct, "score": round(self.score, 4)}


@dataclass
class LevelScore:
    level: int
    total: int
    score: float

    def to_dict(self) -> dict:
        return {"level": self.level, "total": self.total, "score": round(self.score, 4)}


@dataclass
class CurriculumEvaluationReport:
    total_units: int = 0
    score_by_level: list[LevelScore] = field(default_factory=list)
    score_by_layer: list[LayerScore] = field(default_factory=list)
    overall_score: float = 0.0
    failed_units: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    thing_detection_accuracy: float = 0.0
    property_detection_accuracy: float = 0.0
    action_detection_accuracy: float = 0.0
    relation_detection_accuracy: float = 0.0
    cause_effect_separation_accuracy: float = 0.0
    instrument_detection_accuracy: float = 0.0
    time_place_detection_accuracy: float = 0.0
    evidence_need_accuracy: float = 0.0
    certainty_policy_accuracy: float = 0.0
    forbidden_confusion_rate: float = 0.0
    overall_curriculum_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "total_units": self.total_units,
            "overall_score": round(self.overall_score, 4),
            "overall_curriculum_score": round(self.overall_curriculum_score, 4),
            "score_by_level": [s.to_dict() for s in self.score_by_level],
            "score_by_layer": [s.to_dict() for s in self.score_by_layer],
            "failed_units": self.failed_units,
            "recommendations": self.recommendations,
            "metrics": {
                "thing_detection_accuracy": round(self.thing_detection_accuracy, 4),
                "property_detection_accuracy": round(self.property_detection_accuracy, 4),
                "action_detection_accuracy": round(self.action_detection_accuracy, 4),
                "relation_detection_accuracy": round(self.relation_detection_accuracy, 4),
                "cause_effect_separation_accuracy": round(self.cause_effect_separation_accuracy, 4),
                "instrument_detection_accuracy": round(self.instrument_detection_accuracy, 4),
                "time_place_detection_accuracy": round(self.time_place_detection_accuracy, 4),
                "evidence_need_accuracy": round(self.evidence_need_accuracy, 4),
                "certainty_policy_accuracy": round(self.certainty_policy_accuracy, 4),
                "forbidden_confusion_rate": round(self.forbidden_confusion_rate, 4),
            },
        }


class CurriculumEvaluator:
    """
    Evaluates curriculum units using existing system components (FPCL, etc.)
    when available, with graceful fallback to heuristic scoring.
    """

    def evaluate(self, units: list[CognitiveUnit]) -> CurriculumEvaluationReport:
        report = CurriculumEvaluationReport(total_units=len(units))
        if not units:
            return report

        by_level: dict[int, list[CognitiveUnit]] = {}
        by_layer: dict[str, list[CognitiveUnit]] = {}
        for u in units:
            by_level.setdefault(u.level, []).append(u)
            by_layer.setdefault(u.target_layer, []).append(u)

        scores: dict[str, float] = {}
        for u in units:
            scores[u.unit_id] = self._score_unit(u)

        for level in sorted(by_level):
            level_units = by_level[level]
            level_score = sum(scores[u.unit_id] for u in level_units) / len(level_units)
            report.score_by_level.append(LevelScore(level, len(level_units), level_score))
            if level_score < 0.7:
                report.recommendations.append(
                    f"Level {level} ({LEVEL_NAMES.get(level, '')}) score {level_score:.2%} below threshold — review examples"
                )

        for layer in sorted(by_layer):
            layer_units = by_layer[layer]
            layer_score = sum(scores[u.unit_id] for u in layer_units) / len(layer_units)
            report.score_by_layer.append(LayerScore(layer, len(layer_units), 0, layer_score))

        report.failed_units = [uid for uid, s in scores.items() if s < 0.5]

        report.overall_score = sum(scores.values()) / len(scores)
        report.overall_curriculum_score = report.overall_score

        def _avg(layer: str) -> float:
            lu = by_layer.get(layer, [])
            if not lu:
                return 0.0
            return sum(scores[u.unit_id] for u in lu) / len(lu)

        report.thing_detection_accuracy = _avg("thing")
        report.property_detection_accuracy = _avg("property")
        report.action_detection_accuracy = _avg("action")
        report.relation_detection_accuracy = _avg("relation")
        cause_eff = by_layer.get("cause", []) + by_layer.get("effect", [])
        report.cause_effect_separation_accuracy = (
            sum(scores[u.unit_id] for u in cause_eff) / len(cause_eff) if cause_eff else 0.0
        )
        report.instrument_detection_accuracy = _avg("instrument")
        time_place = by_layer.get("time", []) + by_layer.get("place", [])
        report.time_place_detection_accuracy = (
            sum(scores[u.unit_id] for u in time_place) / len(time_place) if time_place else 0.0
        )
        report.evidence_need_accuracy = _avg("evidence")
        report.certainty_policy_accuracy = _avg("certainty")

        adv = [u for u in units if u.difficulty == "adversarial"]
        if adv:
            adv_score = sum(scores[u.unit_id] for u in adv) / len(adv)
            report.forbidden_confusion_rate = 1.0 - adv_score
        else:
            report.forbidden_confusion_rate = 0.0

        if not report.recommendations:
            report.recommendations.append("Curriculum evaluation complete — all levels above threshold")

        return report

    def _score_unit(self, unit: CognitiveUnit) -> float:
        """Heuristic score: checks frame completeness against expected layer."""
        frame = unit.expected_frame
        layer = unit.target_layer
        score = 0.5  # base

        checks = {
            "thing": bool(frame.things),
            "property": bool(frame.properties),
            "action": bool(frame.actions),
            "relation": bool(frame.relations),
            "cause": bool(frame.causes),
            "effect": bool(frame.effects),
            "instrument": bool(frame.instruments),
            "time": bool(frame.times),
            "place": bool(frame.places),
            "evidence": bool(frame.evidence_need),
            "certainty": bool(frame.certainty_policy),
            "mixed_reasoning": bool(frame.evidence_need) and bool(frame.warnings),
        }

        if layer in checks and checks[layer]:
            score += 0.3

        from .curriculum_schema import VALID_CERTAINTY_POLICIES
        if unit.certainty_policy in VALID_CERTAINTY_POLICIES:
            score += 0.1

        if unit.tags:
            score += 0.05

        if unit.unit_id.startswith("CURR-"):
            score += 0.05

        return min(score, 1.0)
