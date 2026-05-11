from mcd.math_governance import ConceptCenterMemory, ConceptCenterRecord


def test_ambiguous_surface_returns_multiple_centers():
    mem = ConceptCenterMemory()
    mem.add_record(ConceptCenterRecord(concept_id="c1", surfaces=["رفع"], roots=["ر ف ع"]))
    mem.add_record(ConceptCenterRecord(concept_id="c2", surfaces=["رفع"], roots=["ر ف ع"]))
    assert len(mem.search_by_surface("رفع")) == 2


def test_concept_center_no_certificate_alone():
    assert ConceptCenterMemory.can_certify_alone() is False
