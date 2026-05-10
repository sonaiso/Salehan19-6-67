"""Tests for mcd.adapters package."""
import json

import pytest

from mcd.adapters.database_adapter import DatabaseAdapter, InMemoryDatabaseAdapter
from mcd.adapters.file_adapter import FileAdapter
from mcd.adapters.llm_adapter import LLMAdapter, MockLLMAdapter
from mcd.adapters.source_adapter import SourceAdapter, StaticSourceAdapter
from mcd.core.certainty import Certainty
from mcd.core.evidence import Evidence
from mcd.knowledge.facts import Fact
from mcd.knowledge.things import Thing


def test_database_adapter_interface_raises_not_implemented():
    adapter = DatabaseAdapter()
    with pytest.raises(NotImplementedError):
        adapter.store("k", {"v": 1})
    with pytest.raises(NotImplementedError):
        adapter.retrieve("k")
    with pytest.raises(NotImplementedError):
        adapter.list_keys()


def test_in_memory_database_adapter_store_retrieve_and_list():
    adapter = InMemoryDatabaseAdapter()
    adapter.store("thing:1", {"name": "foo"})
    adapter.store("fact:1", {"claim": "bar"})
    adapter.store("thing:2", {"name": "baz"})

    assert adapter.retrieve("thing:1") == {"name": "foo"}
    assert adapter.retrieve("missing") is None
    assert set(adapter.list_keys()) == {"thing:1", "fact:1", "thing:2"}
    assert set(adapter.list_keys(prefix="thing:")) == {"thing:1", "thing:2"}


def test_source_adapter_interface_raises_not_implemented():
    adapter = SourceAdapter()
    with pytest.raises(NotImplementedError):
        adapter.fetch("query")
    with pytest.raises(NotImplementedError):
        adapter.get_reliability()


def test_static_source_adapter_fetch_case_insensitive_and_reliability():
    adapter = StaticSourceAdapter(
        data=[
            {"title": "Arabic Grammar", "tag": "linguistics"},
            {"title": "Physics", "tag": "science"},
            {"title": "Fiqh Methods", "tag": "usul"},
        ],
        reliability=0.91,
    )
    assert adapter.get_reliability() == 0.91
    assert adapter.fetch("grammar") == [{"title": "Arabic Grammar", "tag": "linguistics"}]
    assert adapter.fetch("USUL") == [{"title": "Fiqh Methods", "tag": "usul"}]
    assert adapter.fetch("nonexistent") == []


def test_llm_adapter_interface_raises_not_implemented():
    adapter = LLMAdapter()
    with pytest.raises(NotImplementedError):
        adapter.generate_candidates("prompt")
    with pytest.raises(NotImplementedError):
        adapter.summarize("text")
    with pytest.raises(NotImplementedError):
        adapter.compare("a", "b")


def test_mock_llm_adapter_behaviors():
    adapter = MockLLMAdapter()

    candidates = adapter.generate_candidates("Some prompt")
    assert candidates == [{"candidate": "Some prompt", "confidence": 0.5}]

    summary = adapter.summarize("x" * 80)
    assert summary.startswith("[Mock summary of: ")
    assert "x" * 50 in summary

    assert adapter.compare("same", "same") == {"similar": True, "confidence": 0.5}
    assert adapter.compare("a", "b") == {"similar": False, "confidence": 0.5}


def _make_thing() -> Thing:
    return Thing(
        thing_id="thing-1",
        names={"ar": "كتاب", "en": "book"},
        haqiqa="مفهوم يدل على نص مكتوب",
        properties=["readable", "portable"],
        effects=["learning"],
        affordances=["study"],
        relations=["used_by:student"],
        evidence=[
            Evidence(
                source_id="src-1",
                source_type="textual",
                description="Classical reference",
                strength=0.9,
                reliability=0.8,
            )
        ],
        certainty=Certainty(
            score=0.77,
            level="strong_knowledge",
            evidence_type="textual",
            explanation="Multiple corroborated sources",
        ),
    )


def _make_fact() -> Fact:
    return Fact(
        fact_id="fact-1",
        claim="The statement is context dependent.",
        source_ids=["src-1", "src-2"],
        relations=["supports:fact-0"],
        evidence=[
            Evidence(
                source_id="src-2",
                source_type="logical",
                description="Deductive linkage",
                strength=0.7,
                reliability=0.85,
            )
        ],
        certainty=Certainty(
            score=0.66,
            level="probable_knowledge",
            evidence_type="logical",
            explanation="Reasoned derivation",
        ),
    )


def test_file_adapter_save_and_load_things_round_trip(tmp_path):
    adapter = FileAdapter()
    path = tmp_path / "things.json"
    things = [_make_thing()]

    adapter.save_things(things, str(path))
    loaded = adapter.load_things(str(path))

    assert len(loaded) == 1
    loaded_thing = loaded[0]
    assert loaded_thing.thing_id == "thing-1"
    assert loaded_thing.names["ar"] == "كتاب"
    assert loaded_thing.haqiqa == "مفهوم يدل على نص مكتوب"
    assert loaded_thing.evidence[0].source_id == "src-1"
    assert loaded_thing.certainty.score == 0.77
    assert loaded_thing.certainty.level == "strong_knowledge"


def test_file_adapter_load_things_defaults_for_missing_fields(tmp_path):
    adapter = FileAdapter()
    path = tmp_path / "things-minimal.json"
    payload = [{"thing_id": "t-min"}]
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = adapter.load_things(str(path))

    assert len(loaded) == 1
    t = loaded[0]
    assert t.thing_id == "t-min"
    assert t.names == {}
    assert t.haqiqa == ""
    assert t.properties == []
    assert t.evidence == []
    assert t.certainty.score == 0.5
    assert t.certainty.level == "hypothesis"
    assert t.certainty.evidence_type == "unknown"
    assert t.certainty.explanation == ""


def test_file_adapter_save_and_load_facts_round_trip(tmp_path):
    adapter = FileAdapter()
    path = tmp_path / "facts.json"
    facts = [_make_fact()]

    adapter.save_facts(facts, str(path))
    loaded = adapter.load_facts(str(path))

    assert len(loaded) == 1
    loaded_fact = loaded[0]
    assert loaded_fact.fact_id == "fact-1"
    assert loaded_fact.claim == "The statement is context dependent."
    assert loaded_fact.source_ids == ["src-1", "src-2"]
    assert loaded_fact.evidence[0].source_type == "logical"
    assert loaded_fact.certainty.level == "probable_knowledge"


def test_file_adapter_load_facts_defaults_for_missing_fields(tmp_path):
    adapter = FileAdapter()
    path = tmp_path / "facts-minimal.json"
    payload = [{"fact_id": "f-min"}]
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = adapter.load_facts(str(path))

    assert len(loaded) == 1
    f = loaded[0]
    assert f.fact_id == "f-min"
    assert f.claim == ""
    assert f.source_ids == []
    assert f.relations == []
    assert f.evidence == []
    assert f.certainty.score == 0.5
    assert f.certainty.level == "hypothesis"
    assert f.certainty.evidence_type == "unknown"
    assert f.certainty.explanation == ""
