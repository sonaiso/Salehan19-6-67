from __future__ import annotations

from dataclasses import dataclass

from mcd.patterns.bridges import BridgePattern
from mcd.patterns.core import MinimumCompletion, Pattern
from mcd.patterns.meta_pattern import MetaPattern


@dataclass(frozen=True)
class ClosureDefinition:
    closure_id: str
    layer: str
    closure_function: str
    minimum_completion_id: str


@dataclass(frozen=True)
class LayerPatternBinding:
    layer: str
    governor: str
    closure_id: str
    minimum_completion_id: str
    pattern_ids: tuple[str, ...]
    bridge_ids: tuple[str, ...]


class PatternRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Pattern] = {}

    def register(self, pattern: Pattern) -> None:
        self._items[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> Pattern | None:
        return self._items.get(pattern_id)

    def all(self) -> list[Pattern]:
        return list(self._items.values())


class MetaPatternRegistry:
    def __init__(self) -> None:
        self._items: dict[str, MetaPattern] = {}

    def register(self, meta: MetaPattern) -> None:
        self._items[meta.meta_id] = meta

    def get(self, meta_id: str) -> MetaPattern | None:
        return self._items.get(meta_id)


class MinimumCompletionRegistry:
    def __init__(self) -> None:
        self._items: dict[str, MinimumCompletion] = {}

    def register(self, minimum_completion: MinimumCompletion) -> None:
        self._items[minimum_completion.mc_id] = minimum_completion

    def get(self, mc_id: str) -> MinimumCompletion | None:
        return self._items.get(mc_id)


class ClosureRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ClosureDefinition] = {}

    def register(self, definition: ClosureDefinition) -> None:
        self._items[definition.closure_id] = definition

    def get(self, closure_id: str) -> ClosureDefinition | None:
        return self._items.get(closure_id)


class BridgeRegistry:
    def __init__(self) -> None:
        self._items: dict[str, BridgePattern] = {}

    def register(self, bridge: BridgePattern) -> None:
        self._items[bridge.bridge_id] = bridge

    def get(self, bridge_id: str) -> BridgePattern | None:
        return self._items.get(bridge_id)

    def find(self, source_layer: str, target_layer: str) -> BridgePattern | None:
        for bridge in self._items.values():
            if bridge.source_layer == source_layer and bridge.target_layer == target_layer:
                return bridge
        return None


class LayerPatternRegistry:
    def __init__(self) -> None:
        self._items: dict[str, LayerPatternBinding] = {}

    def register(self, binding: LayerPatternBinding) -> None:
        self._items[binding.layer] = binding

    def get(self, layer: str) -> LayerPatternBinding | None:
        return self._items.get(layer)

    def all(self) -> list[LayerPatternBinding]:
        return list(self._items.values())
