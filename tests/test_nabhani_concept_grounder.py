"""Tests for ConceptGrounder."""
from __future__ import annotations

import pytest

from mcd.nabhani.concept_grounder import ConceptGrounder, GROUNDING_THRESHOLD


@pytest.fixture
def grounder():
    return ConceptGrounder()


class TestConceptGrounderRequiresRealityGrounding:
    def test_unknown_word_is_ungrounded(self, grounder):
        result = grounder.ground("شيءمجهول")
        assert result.status == "ungrounded"
        assert result.certainty < GROUNDING_THRESHOLD

    def test_concept_has_id(self, grounder):
        result = grounder.ground("شيء")
        assert result.concept_id.startswith("concept_")

    def test_grounded_when_store_has_thing(self, grounder):
        # Build a minimal mock store
        class MockThings:
            def find_by_name(self, name):
                if name in ("نار", "ار"):
                    class T:
                        name = "نار"
                    return [T()]
                return []

        class MockStore:
            things = MockThings()
            facts = type("F", (), {"find_by_claim": lambda self, x: []})()

            def query_things_by_name(self, name):
                return self.things.find_by_name(name)

            def query_relations(self, source_id="", target_id=""):
                return []

        result = grounder.ground("نار", MockStore())
        assert result.status == "grounded"
        assert result.certainty >= GROUNDING_THRESHOLD
        assert result.grounded_reality is not None

    def test_ungrounded_certainty_is_low(self, grounder):
        result = grounder.ground("مصطلح_خيالي_غير_موجود")
        assert result.certainty < GROUNDING_THRESHOLD

    def test_status_values_are_valid(self, grounder):
        result = grounder.ground("كلمة")
        assert result.status in ("grounded", "partially_grounded", "ungrounded")
