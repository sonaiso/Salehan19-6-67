"""PriorKnowledgeStore — central knowledge repository."""
from __future__ import annotations

import copy
from mcd.knowledge.things import Thing, ThingRegistry
from mcd.knowledge.properties import Property, PropertyRegistry
from mcd.knowledge.facts import Fact, FactStore
from mcd.knowledge.sources import Source
from mcd.core.relations import Relation
from mcd.core.nodes import KnowledgeNode
from mcd.core.certainty import Certainty
from mcd.core.measures import clamp


class PriorKnowledgeStore:
    def __init__(self) -> None:
        self.things = ThingRegistry()
        self.properties = PropertyRegistry()
        self.facts = FactStore()
        self.sources: dict[str, Source] = {}
        self.relations: dict[str, Relation] = {}
        self.concepts: dict[str, KnowledgeNode] = {}
        self.claims: dict[str, KnowledgeNode] = {}
        self.verified: dict[str, KnowledgeNode] = {}
        self._history: list[dict] = []

    def add_thing(self, thing: Thing) -> None:
        self.things.add(thing)

    def add_relation(self, relation: Relation) -> None:
        self.relations[relation.relation_id] = relation

    def add_fact(self, fact: Fact) -> None:
        self.facts.add(fact)

    def add_source(self, source: Source) -> None:
        self.sources[source.source_id] = source

    def query_things_by_name(self, name: str) -> list[Thing]:
        return self.things.find_by_name(name)

    def query_relations(
        self,
        source_id: str = "",
        target_id: str = "",
        relation_type: str = "",
    ) -> list[Relation]:
        results = []
        for rel in self.relations.values():
            if source_id and rel.source != source_id:
                continue
            if target_id and rel.target != target_id:
                continue
            if relation_type and rel.relation_type != relation_type:
                continue
            results.append(rel)
        return results

    def store_hypothesis(self, node: KnowledgeNode) -> None:
        self.claims[node.node_id] = node
        self._history.append({"action": "store_hypothesis", "node_id": node.node_id})

    def promote_to_verified(self, node_id: str) -> None:
        node = self.claims.pop(node_id, None)
        if node is None:
            node = self.concepts.get(node_id)
        if node is not None:
            self.verified[node_id] = node
            self._history.append({"action": "promote_to_verified", "node_id": node_id})

    def update_certainty(self, node_id: str, delta: float, reason: str = "") -> None:
        for store in (self.claims, self.verified, self.concepts):
            if node_id in store:
                node = store[node_id]
                if node.certainty is not None:
                    new_score = clamp(node.certainty.score + delta)
                    node.certainty = Certainty.from_score(new_score, node.certainty.evidence_type, reason)
                self._history.append({"action": "update_certainty", "node_id": node_id, "delta": delta, "reason": reason})
                return

    def snapshot(self) -> dict:
        return {
            "things": [t.thing_id for t in self.things.all()],
            "properties": [p.property_id for p in self.properties.all()],
            "facts": [f.fact_id for f in self.facts.all()],
            "sources": list(self.sources.keys()),
            "relations": list(self.relations.keys()),
            "concepts": list(self.concepts.keys()),
            "claims": list(self.claims.keys()),
            "verified": list(self.verified.keys()),
            "history_len": len(self._history),
        }
