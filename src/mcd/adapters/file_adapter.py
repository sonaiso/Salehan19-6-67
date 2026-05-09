"""File adapter for JSON knowledge files."""
from __future__ import annotations

import json
from mcd.knowledge.things import Thing
from mcd.knowledge.facts import Fact
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty


class FileAdapter:

    def load_things(self, path: str) -> list[Thing]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        things = []
        for d in data:
            evidence = [Evidence(**e) for e in d.get("evidence", [])]
            cert_data = d.get("certainty", {})
            certainty = Certainty(
                score=cert_data.get("score", 0.5),
                level=cert_data.get("level", "hypothesis"),
                evidence_type=cert_data.get("evidence_type", "unknown"),
                explanation=cert_data.get("explanation", ""),
            )
            things.append(Thing(
                thing_id=d["thing_id"],
                names=d.get("names", {}),
                haqiqa=d.get("haqiqa", ""),
                properties=d.get("properties", []),
                effects=d.get("effects", []),
                affordances=d.get("affordances", []),
                relations=d.get("relations", []),
                evidence=evidence,
                certainty=certainty,
            ))
        return things

    def save_things(self, things: list[Thing], path: str) -> None:
        data = []
        for t in things:
            data.append({
                "thing_id": t.thing_id,
                "names": t.names,
                "haqiqa": t.haqiqa,
                "properties": t.properties,
                "effects": t.effects,
                "affordances": t.affordances,
                "relations": t.relations,
                "evidence": [{"source_id": e.source_id, "source_type": e.source_type, "description": e.description, "strength": e.strength, "reliability": e.reliability} for e in t.evidence],
                "certainty": {"score": t.certainty.score, "level": t.certainty.level, "evidence_type": t.certainty.evidence_type, "explanation": t.certainty.explanation},
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_facts(self, path: str) -> list[Fact]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        facts = []
        for d in data:
            evidence = [Evidence(**e) for e in d.get("evidence", [])]
            cert_data = d.get("certainty", {})
            certainty = Certainty(
                score=cert_data.get("score", 0.5),
                level=cert_data.get("level", "hypothesis"),
                evidence_type=cert_data.get("evidence_type", "unknown"),
                explanation=cert_data.get("explanation", ""),
            )
            facts.append(Fact(
                fact_id=d["fact_id"],
                claim=d.get("claim", ""),
                source_ids=d.get("source_ids", []),
                relations=d.get("relations", []),
                evidence=evidence,
                certainty=certainty,
            ))
        return facts

    def save_facts(self, facts: list[Fact], path: str) -> None:
        data = []
        for f in facts:
            data.append({
                "fact_id": f.fact_id,
                "claim": f.claim,
                "source_ids": f.source_ids,
                "relations": f.relations,
                "evidence": [{"source_id": e.source_id, "source_type": e.source_type, "description": e.description, "strength": e.strength, "reliability": e.reliability} for e in f.evidence],
                "certainty": {"score": f.certainty.score, "level": f.certainty.level, "evidence_type": f.certainty.evidence_type, "explanation": f.certainty.explanation},
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
