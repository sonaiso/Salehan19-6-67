"""RelationBuilder: extract relations from text and nodes."""
from __future__ import annotations

import uuid
from mcd.core.nodes import KnowledgeNode
from mcd.core.relations import Relation, RelationType
from mcd.core.symbols import is_arabic_letter


class RelationBuilder:

    def __init__(self, store=None) -> None:
        self._store = store

    def build_relations(self, text: str, nodes: list[KnowledgeNode]) -> list[Relation]:
        words = [w for w in text.split() if w]
        relations: list[Relation] = []

        # has_root relations for each word node
        for node in nodes:
            if node.level == "word":
                root = node.features.get("root", "")
                if root:
                    rel = Relation(
                        relation_id=f"rel_root_{uuid.uuid4().hex[:8]}",
                        relation_type=RelationType.HAS_ROOT.value,
                        source=node.node_id,
                        target=root,
                        certainty=0.80,
                    )
                    relations.append(rel)

        # Verb-subject-object detection
        vso_rels = self._detect_verb_subject_object(words)
        relations.extend(vso_rels)

        # Link words to known things
        if self._store:
            for node in nodes:
                if node.level == "word":
                    thing_rels = self._link_to_things(node.surface, nodes)
                    relations.extend(thing_rels)

        return relations

    def _detect_verb_subject_object(self, words: list[str]) -> list[Relation]:
        relations = []
        if len(words) >= 2:
            # Heuristic: first word = verb (if short), second = agent, third = patient
            verb = words[0]
            stripped_verb = verb.replace('ال', '').strip()

            if len(words) >= 2:
                subject = words[1]
                # agent_of relation
                relations.append(Relation(
                    relation_id=f"rel_agent_{uuid.uuid4().hex[:8]}",
                    relation_type=RelationType.AGENT_OF.value,
                    source=subject,
                    target=verb,
                    certainty=0.65,
                ))

            if len(words) >= 3:
                obj = words[2]
                relations.append(Relation(
                    relation_id=f"rel_patient_{uuid.uuid4().hex[:8]}",
                    relation_type=RelationType.PATIENT_OF.value,
                    source=obj,
                    target=verb,
                    certainty=0.65,
                ))

        return relations

    def _link_to_things(self, word: str, nodes: list[KnowledgeNode]) -> list[Relation]:
        if not self._store:
            return []
        relations = []
        clean = word.replace('ال', '').replace('ة', '').strip()
        things = self._store.query_things_by_name(clean) + self._store.query_things_by_name(word)
        seen = set()
        for thing in things:
            if thing.thing_id not in seen:
                seen.add(thing.thing_id)
                relations.append(Relation(
                    relation_id=f"rel_denotes_{uuid.uuid4().hex[:8]}",
                    relation_type=RelationType.DENOTES.value,
                    source=word,
                    target=thing.thing_id,
                    certainty=0.80,
                ))
        return relations
