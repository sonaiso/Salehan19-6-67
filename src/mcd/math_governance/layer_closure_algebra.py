from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS, collapse_to_public_judgment
from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit
from mcd.math_governance.level_morphism_registry import LevelMorphismRegistry
from mcd.math_governance.level_schema import ALL_LEVELS
from mcd.math_governance.text_ascent_chain import validate_text_ascent_chain

Judgment = str

ZERO = "zero"
HYPOTHESIS = "hypothesis"
CERTIFICATE = "certificate"
NON_DERIVATIONAL_DEFAULT_CATEGORIES = {
    "mabni",
    "pronoun",
    "demonstrative",
    "relative",
    "particle",
    "proper_noun",
    "loanword",
    "term",
    "heard_form",
}


def _normalize_judgment(value: str) -> str:
    return collapse_to_public_judgment(value)


@dataclass(frozen=True)
class LayerContract:
    layer_id: str
    domain: str
    scope: str
    rank: int
    prerequisites: list[str] = field(default_factory=list)
    residual_rules: list[str] = field(default_factory=lambda: ["preserve"])
    fatal_barriers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BridgeContract:
    bridge_id: str
    source_layer: str
    target_layer: str
    allowed_input: list[str] = field(default_factory=list)
    required_evidence_rank: int = 0
    preserved_residuals: bool = True
    governor: str = "default"
    bridge_barriers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LocalCertificate:
    layer_id: str
    judgment: Judgment
    minimum_completeness: bool
    closure: bool
    fatal_barrier: bool
    reasons: list[str] = field(default_factory=list)

    @property
    def certified(self) -> bool:
        return self.judgment == CERTIFICATE


@dataclass(frozen=True)
class BridgeEvaluation:
    bridge_id: str
    source_layer: str
    target_layer: str
    passed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GlobalCertificateResult:
    judgment: Judgment
    passed: bool
    local_certificates: dict[str, LocalCertificate]
    bridge_evaluations: list[BridgeEvaluation]
    scope_defined: bool
    residuals_preserved: bool
    replayable_trace: bool
    no_fatal_barrier: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class JudgmentVector:
    layer_judgments: dict[str, Judgment]
    global_judgment: Judgment
    local_certificates: dict[str, LocalCertificate]
    bridge_evaluations: list[BridgeEvaluation]
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "layer_judgments": self.layer_judgments,
            "global_judgment": self.global_judgment,
            "local_certificates": {
                layer: {
                    "judgment": cert.judgment,
                    "minimum_completeness": cert.minimum_completeness,
                    "closure": cert.closure,
                    "fatal_barrier": cert.fatal_barrier,
                    "reasons": cert.reasons,
                }
                for layer, cert in self.local_certificates.items()
            },
            "bridge_evaluations": [
                {
                    "bridge_id": bridge.bridge_id,
                    "source_layer": bridge.source_layer,
                    "target_layer": bridge.target_layer,
                    "passed": bridge.passed,
                    "reasons": bridge.reasons,
                }
                for bridge in self.bridge_evaluations
            ],
            "reasons": self.reasons,
        }


class LayerRegistry:
    def __init__(self) -> None:
        self._layers: dict[str, LayerContract] = {}
        level_names = [level.name for level in ALL_LEVELS]
        for i, level in enumerate(ALL_LEVELS):
            prerequisites = [level_names[i - 1]] if i > 0 else []
            self.register(
                LayerContract(
                    layer_id=level.name,
                    domain=level.name,
                    scope=level.name,
                    rank=level.order,
                    prerequisites=prerequisites,
                    residual_rules=["preserve", "no_silent_drop"],
                    fatal_barriers=[],
                )
            )

    def register(self, contract: LayerContract) -> None:
        self._layers[contract.layer_id] = contract

    def get(self, layer_id: str) -> LayerContract | None:
        return self._layers.get(layer_id)

    def all(self) -> list[LayerContract]:
        return sorted(self._layers.values(), key=lambda layer: layer.rank)


class ClosureRegistry:
    def __init__(self) -> None:
        self._minimum_checks: dict[str, Callable[[GovernedFractalUnit], bool]] = {}
        self._closure_checks: dict[str, Callable[[GovernedFractalUnit], bool]] = {}

    def register(
        self,
        layer_id: str,
        minimum_check: Callable[[GovernedFractalUnit], bool],
        closure_check: Callable[[GovernedFractalUnit], bool] | None = None,
    ) -> None:
        self._minimum_checks[layer_id] = minimum_check
        self._closure_checks[layer_id] = closure_check or minimum_check

    @staticmethod
    def _default_check(unit: GovernedFractalUnit) -> bool:
        return (
            bool(unit.level_id)
            and bool(unit.unit_type)
            and bool(unit.raw_text)
            and bool(unit.normalized_text)
            and bool(unit.trace_refs)
            and unit.beta_status in {"valid_uncertified", "valid_certified"}
        )

    def ensure_default(self, layer_id: str) -> None:
        if layer_id in self._minimum_checks:
            return
        self.register(layer_id, self._default_check, self._default_check)

    def evaluate(self, layer_id: str, unit: GovernedFractalUnit) -> tuple[bool, bool]:
        self.ensure_default(layer_id)
        minimum = self._minimum_checks[layer_id](unit)
        closure = self._closure_checks[layer_id](unit)
        return minimum, closure


class ResidualRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, list[str]] = {}

    def register(self, layer_id: str, rules: list[str]) -> None:
        self._rules[layer_id] = list(dict.fromkeys(rules))

    def get(self, layer_id: str) -> list[str]:
        return self._rules.get(layer_id, ["preserve"])


class PatternRegistry:
    def __init__(self) -> None:
        self._patterns: dict[str, list[str]] = {}

    def register(self, layer_id: str, patterns: list[str]) -> None:
        self._patterns[layer_id] = patterns

    def get(self, layer_id: str) -> list[str]:
        return self._patterns.get(layer_id, [])


class GovernorRegistry:
    def __init__(self) -> None:
        self._governors: dict[str, str] = {}

    def register(self, layer_id: str, governor_id: str) -> None:
        self._governors[layer_id] = governor_id

    def get(self, layer_id: str) -> str:
        return self._governors.get(layer_id, "default")


class BridgeRegistry:
    def __init__(self, morphisms: LevelMorphismRegistry | None = None) -> None:
        self._bridges: dict[str, BridgeContract] = {}
        self._morphisms = morphisms or LevelMorphismRegistry()
        for morphism in self._morphisms.get_all():
            self.register(
                BridgeContract(
                    bridge_id=morphism.morphism_id,
                    source_layer=morphism.source_level,
                    target_layer=morphism.target_level,
                    allowed_input=list(morphism.source_unit_types),
                    required_evidence_rank=0,
                    preserved_residuals=morphism.preserves.get("residual", True),
                    governor="default",
                    bridge_barriers=[],
                )
            )

    def register(self, bridge: BridgeContract) -> None:
        self._bridges[bridge.bridge_id] = bridge

    def find(self, source_layer: str, target_layer: str) -> BridgeContract | None:
        for bridge in self._bridges.values():
            if bridge.source_layer == source_layer and bridge.target_layer == target_layer:
                return bridge
        return None

    def all(self) -> list[BridgeContract]:
        return list(self._bridges.values())


class NonDerivationalTree:
    def __init__(self) -> None:
        self._categories = set(NON_DERIVATIONAL_DEFAULT_CATEGORIES)

    def is_non_derivational(self, unit: GovernedFractalUnit) -> bool:
        tags = {unit.unit_type.lower(), unit.level_id.lower(), *(str(x).lower() for x in unit.invariants)}
        metadata_tag = str(unit.metadata.get("non_derivational_category", "")).lower()
        return bool((tags & self._categories) or metadata_tag in self._categories)


class LayerClosureAlgebra:
    def __init__(
        self,
        *,
        layer_registry: LayerRegistry | None = None,
        closure_registry: ClosureRegistry | None = None,
        bridge_registry: BridgeRegistry | None = None,
        residual_registry: ResidualRegistry | None = None,
        governor_registry: GovernorRegistry | None = None,
        pattern_registry: PatternRegistry | None = None,
        non_derivational_tree: NonDerivationalTree | None = None,
    ) -> None:
        self.layer_registry = layer_registry or LayerRegistry()
        self.closure_registry = closure_registry or ClosureRegistry()
        self.bridge_registry = bridge_registry or BridgeRegistry()
        self.residual_registry = residual_registry or ResidualRegistry()
        self.governor_registry = governor_registry or GovernorRegistry()
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.non_derivational_tree = non_derivational_tree or NonDerivationalTree()

    def _evaluate_local(self, unit: GovernedFractalUnit) -> LocalCertificate:
        minimum, closure = self.closure_registry.evaluate(unit.level_id, unit)
        reasons: list[str] = []
        fatal = False

        if minimum != closure:
            reasons.append(f"{unit.level_id}: χ_L must be equivalent to MC_L")
            fatal = True
        if unit.metadata.get("fatal_barrier", False):
            reasons.append(f"{unit.level_id}: fatal barrier present")
            fatal = True

        if fatal:
            judgment = ZERO
        elif minimum and closure:
            judgment = CERTIFICATE
        else:
            in_domain = bool(unit.level_id)
            judgment = HYPOTHESIS if in_domain else ZERO

        if unit.level_id == "root" and self.non_derivational_tree.is_non_derivational(unit):
            reasons.append("layered_zero_allowed_non_derivational_path")
            if judgment == ZERO:
                judgment = HYPOTHESIS

        return LocalCertificate(
            layer_id=unit.level_id,
            judgment=judgment,
            minimum_completeness=minimum,
            closure=closure,
            fatal_barrier=fatal,
            reasons=reasons,
        )

    def _evaluate_bridges(
        self,
        layer_order: list[str],
        local: dict[str, LocalCertificate],
        units_by_layer: dict[str, GovernedFractalUnit],
    ) -> list[BridgeEvaluation]:
        evaluations: list[BridgeEvaluation] = []
        for i in range(len(layer_order) - 1):
            source = layer_order[i]
            target = layer_order[i + 1]
            bridge = self.bridge_registry.find(source, target)
            reasons: list[str] = []
            if bridge is None:
                evaluations.append(
                    BridgeEvaluation(
                        bridge_id=f"{source}_to_{target}",
                        source_layer=source,
                        target_layer=target,
                        passed=False,
                        reasons=[f"missing bridge contract for {source}->{target}"],
                    )
                )
                continue

            source_cert = local.get(source)
            target_cert = local.get(target)
            source_unit = units_by_layer[source]
            target_unit = units_by_layer[target]

            passed = True
            if source_cert is None or target_cert is None:
                passed = False
                reasons.append("missing source/target local certificate")
            if source_cert and source_cert.judgment != CERTIFICATE:
                passed = False
                reasons.append(f"{source}: source layer not locally certified")
            source_output_type = str(source_unit.metadata.get("output_type", source_unit.unit_type)).strip()
            if source_unit.level_id not in bridge.allowed_input and source_output_type not in bridge.allowed_input:
                passed = False
                reasons.append(f"{bridge.bridge_id}: output not acceptable for target")
            target_contract = self.layer_registry.get(target)
            if target_contract and target_contract.rank < bridge.required_evidence_rank:
                passed = False
                reasons.append(f"{bridge.bridge_id}: evidence rank requirement not met")
            if source_unit.unit_id not in target_unit.pre_unit_ids:
                passed = False
                reasons.append(f"{bridge.bridge_id}: missing pre link from target to source")
            if target_unit.unit_id not in source_unit.post_unit_ids:
                passed = False
                reasons.append(f"{bridge.bridge_id}: missing post link from source to target")
            if bridge.preserved_residuals:
                missing_residuals = [r for r in source_unit.residuals if r not in target_unit.residuals]
                if missing_residuals:
                    passed = False
                    reasons.append(f"{bridge.bridge_id}: residuals not preserved ({missing_residuals})")
            if target_cert and target_cert.judgment == CERTIFICATE and not passed:
                reasons.append("layer_theft_blocked")
            evaluations.append(
                BridgeEvaluation(
                    bridge_id=bridge.bridge_id,
                    source_layer=source,
                    target_layer=target,
                    passed=passed,
                    reasons=reasons,
                )
            )
        return evaluations

    @staticmethod
    def _residuals_preserved(units: list[GovernedFractalUnit]) -> bool:
        for i in range(len(units) - 1):
            next_residuals = set(units[i + 1].residuals)
            if any(item not in next_residuals for item in units[i].residuals):
                return False
        return True

    @staticmethod
    def _replayable(units: list[GovernedFractalUnit]) -> bool:
        report = validate_text_ascent_chain(units)
        return report.passed

    def evaluate(
        self,
        units: list[GovernedFractalUnit],
        *,
        required_layers: list[str] | None = None,
    ) -> JudgmentVector:
        units_by_layer = {unit.level_id: unit for unit in units}
        ordered_layers = [layer.layer_id for layer in self.layer_registry.all() if layer.layer_id in units_by_layer]
        local = {layer: self._evaluate_local(units_by_layer[layer]) for layer in ordered_layers}
        bridges = self._evaluate_bridges(ordered_layers, local, units_by_layer) if len(ordered_layers) > 1 else []

        required_layers = required_layers or ordered_layers
        reasons: list[str] = []
        required_present = all(layer in local for layer in required_layers)
        if not required_present:
            reasons.append("scope(global) undefined: required layers missing")
        all_local = required_present and all(local[layer].judgment == CERTIFICATE for layer in required_layers)
        if not all_local:
            reasons.append("local certificate requirements not satisfied")

        all_bridges = all(bridge.passed for bridge in bridges)
        if not all_bridges:
            reasons.append("bridge ascend requirements not satisfied")

        residuals_ok = self._residuals_preserved(units)
        if not residuals_ok:
            reasons.append("residuals not preserved globally")

        replayable = self._replayable(units)
        if not replayable:
            reasons.append("trace is not replayable")

        no_fatal = not any(cert.fatal_barrier for cert in local.values())
        if not no_fatal:
            reasons.append("fatal barrier detected")

        global_passed = all([required_present, all_local, all_bridges, residuals_ok, replayable, no_fatal])
        if not required_present or not no_fatal:
            global_judgment = ZERO
        elif global_passed:
            global_judgment = CERTIFICATE
        else:
            global_judgment = HYPOTHESIS
        layer_judgments = {layer: cert.judgment for layer, cert in local.items()}
        layer_judgments["global"] = global_judgment

        return JudgmentVector(
            layer_judgments={layer: _normalize_judgment(judgment) for layer, judgment in layer_judgments.items()},
            global_judgment=_normalize_judgment(global_judgment),
            local_certificates=local,
            bridge_evaluations=bridges,
            reasons=reasons,
        )


def build_default_units_for_text(text: str, *, final_judgment: str = HYPOTHESIS) -> list[GovernedFractalUnit]:
    levels = [level.name for level in ALL_LEVELS]
    units: list[GovernedFractalUnit] = []
    for i, level in enumerate(levels):
        unit_id = f"U-{i + 1:02d}-{level}"
        pre = [f"U-{i:02d}-{levels[i - 1]}"] if i > 0 else []
        post = [f"U-{i + 2:02d}-{levels[i + 1]}"] if i < len(levels) - 1 else []
        unit_type = final_judgment if level == "final_judgment" else level
        units.append(
            GovernedFractalUnit(
                unit_id=unit_id,
                level_id=level,
                unit_type=unit_type,
                surface=text,
                normalized=text,
                raw_span=(0, len(text)),
                normalized_span=(0, len(text)),
                raw_text=text,
                normalized_text=text,
                pre_unit_ids=pre,
                post_unit_ids=post,
                morphism_in=None if i == 0 else f"{levels[i - 1]}_to_{level}",
                morphism_out=f"{level}_to_{levels[i + 1]}" if i < len(levels) - 1 else None,
                pre_to_post_relation="ascent_step" if post else "",
                trace_refs=["TR-1", "U-000001"],
                residuals=["omega-1"],
                beta_status="valid_uncertified" if post else "valid_certified",
                metadata={"generated_reason": "seed"} if i == 0 else {},
            )
        )
    return units


def local_certificate(unit: GovernedFractalUnit, *, algebra: LayerClosureAlgebra | None = None) -> LocalCertificate:
    return (algebra or LayerClosureAlgebra())._evaluate_local(unit)


def global_certificate(
    units: list[GovernedFractalUnit],
    *,
    required_layers: list[str] | None = None,
    algebra: LayerClosureAlgebra | None = None,
) -> GlobalCertificateResult:
    result = (algebra or LayerClosureAlgebra()).evaluate(units, required_layers=required_layers)
    passed = result.global_judgment == CERTIFICATE
    return GlobalCertificateResult(
        judgment=result.global_judgment,
        passed=passed,
        local_certificates=result.local_certificates,
        bridge_evaluations=result.bridge_evaluations,
        scope_defined=not any(reason.startswith("scope(global) undefined") for reason in result.reasons),
        residuals_preserved=not any("residuals not preserved globally" in reason for reason in result.reasons),
        replayable_trace=not any("trace is not replayable" in reason for reason in result.reasons),
        no_fatal_barrier=not any("fatal barrier" in reason for reason in result.reasons),
        reasons=result.reasons,
    )


def is_public_judgment(value: str) -> bool:
    return _normalize_judgment(value) in PUBLIC_FINAL_JUDGMENTS
