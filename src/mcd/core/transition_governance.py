"""Constitutional transition governance helpers."""
from __future__ import annotations

from dataclasses import dataclass

TRANSITION_LAYER_ORDER: tuple[str, ...] = (
    "definition",
    "classification",
    "interpretation",
    "relation",
    "evidence",
    "inference",
    "judgment",
    "application",
    "trace",
)

LAYER_FUNCTIONS: dict[str, str] = {
    "definition": "designation",
    "classification": "distinction",
    "interpretation": "interpretation",
    "relation": "linking",
    "evidence": "proofing",
    "inference": "reasoning",
    "judgment": "judgment",
    "application": "application",
    "trace": "reconstruction",
}

_LAYER_INDEX = {layer: idx for idx, layer in enumerate(TRANSITION_LAYER_ORDER)}
_SEMANTIC_CORRUPTION_PAIRS = frozenset(
    {
        ("definition", "judgment"),
        ("interpretation", "evidence"),
        ("relation", "inference"),
    }
)


@dataclass(frozen=True)
class TransitionRecord:
    source: str
    target: str
    gate: str
    gate_passed: bool
    allowed: bool
    residual: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "source": self.source,
            "target": self.target,
            "source_function": layer_function(self.source),
            "target_function": layer_function(self.target),
            "gate": self.gate,
            "gate_passed": self.gate_passed,
            "allowed": self.allowed,
            "residual": self.residual,
        }


def layer_function(layer: str) -> str:
    return LAYER_FUNCTIONS.get(_normalize(layer), "unknown")


def assess_transition(source: str, target: str, *, gate: str, gate_passed: bool) -> TransitionRecord:
    src = _normalize(source)
    dst = _normalize(target)
    residual = ""

    if (src, dst) in _SEMANTIC_CORRUPTION_PAIRS:
        residual = "invalid_semantic_transition"
    elif _is_upward(dst, src) and not _is_adjacent_upward(src, dst):
        residual = "invalid_semantic_transition"
    elif not gate_passed:
        residual = "gate_blocked"

    return TransitionRecord(
        source=src,
        target=dst,
        gate=gate,
        gate_passed=gate_passed,
        allowed=not residual,
        residual=residual,
    )


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _is_upward(target: str, source: str) -> bool:
    target_idx = _LAYER_INDEX.get(target)
    source_idx = _LAYER_INDEX.get(source)
    if target_idx is None or source_idx is None:
        return False
    return target_idx > source_idx


def _is_adjacent_upward(source: str, target: str) -> bool:
    src_idx = _LAYER_INDEX.get(source)
    dst_idx = _LAYER_INDEX.get(target)
    if src_idx is None or dst_idx is None:
        return False
    return dst_idx == src_idx + 1
