"""csv_loader — loads things.csv and facts.csv into PriorKnowledgeStore.

No core code is changed. This module reads the CSV files from
data/knowledge/ and populates the store using the existing
store.add_thing() and store.add_fact() interfaces.
"""
from __future__ import annotations

import csv
import pathlib
from typing import Optional

from mcd.knowledge.things import Thing
from mcd.knowledge.facts import Fact
from mcd.core.evidence import Evidence, EvidenceType
from mcd.core.certainty import Certainty
from mcd.core.relations import Relation

# Path: src/mcd/knowledge/ → up 3 levels → project root → data/knowledge/
_DATA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "data" / "knowledge"

_THINGS_CSV    = _DATA_DIR / "things.csv"
_FACTS_CSV     = _DATA_DIR / "facts.csv"
_RELATIONS_CSV = _DATA_DIR / "relations.csv"

# Default evidence used for CSV-sourced entries
_EV_CSV = Evidence(
    source_id="src_csv",
    source_type=EvidenceType.LINGUISTIC.value,
    description="مُحمَّل من ملف CSV",
    strength=0.80,
    reliability=0.80,
)


def _split(value: str) -> list[str]:
    """Split a pipe-separated cell into a list, ignoring empty strings."""
    return [v.strip() for v in value.split("|") if v.strip()]


def load_csv_things(store) -> int:
    """Read things.csv and add each row as a Thing to the store.
    Returns the number of things loaded."""
    if not _THINGS_CSV.exists():
        return 0

    count = 0
    with open(_THINGS_CSV, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            thing_id = row.get("thing_id", "").strip()
            name_ar  = row.get("name_ar", "").strip()
            haqiqa   = row.get("haqiqa", "").strip()
            if not thing_id or not name_ar:
                continue

            try:
                score = float(row.get("certainty_score", "0.75"))
            except ValueError:
                score = 0.75
            cert_type = row.get("certainty_type", "linguistic").strip() or "linguistic"

            thing = Thing(
                thing_id=thing_id,
                names={"ar": name_ar},
                haqiqa=haqiqa,
                properties=_split(row.get("properties", "")),
                effects=_split(row.get("effects", "")),
                affordances=_split(row.get("affordances", "")),
                relations=[],
                evidence=[_EV_CSV],
                certainty=Certainty.from_score(score, cert_type),
            )
            store.add_thing(thing)
            count += 1

    return count


def load_csv_facts(store) -> int:
    """Read facts.csv and add each row as a Fact to the store.
    Returns the number of facts loaded."""
    if not _FACTS_CSV.exists():
        return 0

    count = 0
    with open(_FACTS_CSV, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fact_id = row.get("fact_id", "").strip()
            # prefer vocalized form as the canonical claim
            claim = (
                row.get("claim_vocalized", "").strip()
                or row.get("claim", "").strip()
            )
            if not fact_id or not claim:
                continue

            try:
                score = float(row.get("certainty_score", "0.80"))
            except ValueError:
                score = 0.80
            cert_type = row.get("certainty_type", "experimental").strip() or "experimental"

            fact = Fact(
                fact_id=fact_id,
                claim=claim,
                source_ids=["src_csv"],
                evidence=[_EV_CSV],
                certainty=Certainty.from_score(score, cert_type),
            )
            store.add_fact(fact)
            count += 1

    return count


def load_csv_relations(store) -> int:
    """Read relations.csv and add each row as a Relation to the store.
    Returns the number of relations loaded."""
    if not _RELATIONS_CSV.exists():
        return 0

    count = 0
    with open(_RELATIONS_CSV, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            relation_id   = row.get("relation_id", "").strip()
            relation_type = row.get("relation_type", "").strip()
            source        = row.get("source", "").strip()
            target        = row.get("target", "").strip()
            if not all([relation_id, relation_type, source, target]):
                continue

            try:
                certainty = float(row.get("certainty", "0.75"))
            except ValueError:
                certainty = 0.75

            conditions = _split(row.get("conditions", ""))

            rel = Relation(
                relation_id=relation_id,
                relation_type=relation_type,
                source=source,
                target=target,
                conditions=conditions,
                evidence=[_EV_CSV],
                certainty=certainty,
            )
            store.add_relation(rel)
            count += 1

    return count


def load_csv_data(store) -> dict[str, int]:
    """Load all CSV knowledge files into the store.
    Returns a summary dict with counts."""
    return {
        "things":    load_csv_things(store),
        "facts":     load_csv_facts(store),
        "relations": load_csv_relations(store),
    }
