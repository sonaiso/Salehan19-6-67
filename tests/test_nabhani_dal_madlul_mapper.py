"""Tests for DalMadlulMapper."""
from __future__ import annotations

import pytest

from mcd.nabhani.dal_madlul_mapper import DalMadlulMapper


@pytest.fixture
def mapper():
    return DalMadlulMapper()


class TestDalMadlulMapperDistinguishesMeaningFromConcept:
    def test_ungrounded_word_is_not_concept(self, mapper):
        result = mapper.map("بركانوس", "كلمة مجهولة", has_reality=False)
        assert result.concept is None
        assert result.grounding_status == "ungrounded_linguistic_meaning"

    def test_grounded_word_becomes_concept(self, mapper):
        result = mapper.map("نار", "مادة مشتعلة", has_reality=True)
        assert result.concept == "مادة مشتعلة"
        assert result.grounding_status in ("grounded_concept", "verified_concept")

    def test_verified_concept_status(self, mapper):
        result = mapper.map("نار", "مادة مشتعلة", has_reality=True, verified=True)
        assert result.grounding_status == "verified_concept"

    def test_prior_knowledge_partially_grounds(self, mapper):
        result = mapper.map("كتاب", "مؤلَّف مكتوب", has_reality=False, prior_knowledge="الكتب مصادر علم")
        assert result.grounding_status in ("grounded_concept", "partially_grounded")

    def test_dalalah_type_mutabaqa(self, mapper):
        result = mapper.map("نار", "نار", has_reality=True)
        assert result.dalalah_type == "mutabaqa"

    def test_map_text_returns_list(self, mapper):
        results = mapper.map_text("النار تحرق")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_map_text_with_no_store(self, mapper):
        results = mapper.map_text("العلم نور")
        assert all(hasattr(r, "dal") for r in results)
