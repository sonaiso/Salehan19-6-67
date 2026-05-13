"""Layer sovereignty registry for governed meaning-ascent contracts."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.epistemic_rank import EpistemicRank
from mcd.math_governance.level_schema import ALL_LEVELS

_DEFAULT_RESIDUAL_RULES = ("preserve", "no_silent_drop", "no_residual_erasure")


@dataclass(frozen=True)
class LayerSovereigntyEntry:
    layer: str
    governor: str
    allowed_ascent: list[str] = field(default_factory=list)
    forbidden_ascent: list[str] = field(default_factory=list)
    required_evidence: str = "ZERO"
    residual_rules: list[str] = field(default_factory=lambda: list(_DEFAULT_RESIDUAL_RULES))
    closure_function: str = "chi_L_default"
    minimum_completion: str = "MC_L_default"


class LayerSovereigntyRegistry:
    """Registry that encodes layer authority and ascent constraints."""

    def __init__(self) -> None:
        self._entries: dict[str, LayerSovereigntyEntry] = {}
        level_names = [level.name for level in ALL_LEVELS]
        for idx, level in enumerate(ALL_LEVELS):
            allowed = [level_names[idx + 1]] if idx < len(level_names) - 1 else []
            forbidden = level_names[: idx + 1]
            required = self._required_rank_for_layer(level.name)
            self.register(
                LayerSovereigntyEntry(
                    layer=level.name,
                    governor=f"governor.{level.name}",
                    allowed_ascent=allowed,
                    forbidden_ascent=forbidden,
                    required_evidence=required.name,
                    residual_rules=["preserve", "no_silent_drop", "no_residual_erasure"],
                    closure_function=f"chi_{level.name}",
                    minimum_completion=f"MC_{level.name}",
                ),
            )

    @staticmethod
    def _required_rank_for_layer(layer: str) -> EpistemicRank:
        if layer == "final_judgment":
            return EpistemicRank.CERTIFICATE
        if layer in {"evidence", "judgment", "claim"}:
            return EpistemicRank.STRONG_EVIDENCE
        return EpistemicRank.HYPOTHESIS

    def register(self, entry: LayerSovereigntyEntry) -> None:
        self._entries[entry.layer] = entry

    def get(self, layer: str) -> LayerSovereigntyEntry | None:
        return self._entries.get(layer)

    def all(self) -> list[LayerSovereigntyEntry]:
        return [self._entries[level.name] for level in ALL_LEVELS if level.name in self._entries]

    def as_dict(self) -> list[dict[str, object]]:
        return [
            {
                "layer": entry.layer,
                "governor": entry.governor,
                "allowed_ascent": list(entry.allowed_ascent),
                "forbidden_ascent": list(entry.forbidden_ascent),
                "required_evidence": entry.required_evidence,
                "residual_rules": list(entry.residual_rules),
                "closure_function": entry.closure_function,
                "minimum_completion": entry.minimum_completion,
            }
            for entry in self.all()
        ]
