import pytest
from mcd.fractal_kernel import ConceptCenterRecord, ConceptCenterMemory


def make_record(**kwargs):
    defaults = dict(concept_id="CC-001", surface_forms=["كتابة", "كتب"],
                    root_family=["ك ت ب"], essence_axis="writing")
    defaults.update(kwargs)
    return ConceptCenterRecord(**defaults)


def test_add_and_retrieve():
    mem = ConceptCenterMemory()
    rec = make_record()
    mem.add_concept_center(rec)
    assert mem.get_by_concept_id("CC-001") is not None


def test_search_by_surface():
    mem = ConceptCenterMemory()
    rec = make_record()
    mem.add_concept_center(rec)
    results = mem.search_by_surface("كتابة")
    assert len(results) == 1
    assert results[0].concept_id == "CC-001"


def test_search_by_root():
    mem = ConceptCenterMemory()
    rec = make_record()
    mem.add_concept_center(rec)
    results = mem.search_by_root("ك ت ب")
    assert len(results) == 1


def test_link_unit():
    mem = ConceptCenterMemory()
    rec = make_record()
    mem.add_concept_center(rec)
    ok = mem.link_unit_to_concept("CC-001", "CFU-001")
    assert ok is True
    assert "CFU-001" in mem.get_by_concept_id("CC-001").linked_unit_ids


def test_link_unit_not_found():
    mem = ConceptCenterMemory()
    ok = mem.link_unit_to_concept("NONEXISTENT", "CFU-001")
    assert ok is False


def test_export_memory():
    mem = ConceptCenterMemory()
    rec = make_record()
    mem.add_concept_center(rec)
    exported = mem.export_memory()
    assert len(exported) == 1
    assert exported[0]["concept_id"] == "CC-001"


def test_len():
    mem = ConceptCenterMemory()
    assert len(mem) == 0
    mem.add_concept_center(make_record())
    assert len(mem) == 1
