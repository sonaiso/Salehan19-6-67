"""Tests for NabhaniDecoder end-to-end pipeline."""
from __future__ import annotations

import pytest

from mcd.nabhani.nabhani_decoder import NabhaniDecoder


@pytest.fixture(scope="module")
def decoder():
    return NabhaniDecoder()


class TestNabhaniDecoderFireBurns:
    """النار تحرق — sensory epistemic claim."""

    def test_returns_dict(self, decoder):
        result = decoder.decode("النار تحرق")
        assert isinstance(result, dict)

    def test_required_keys_present(self, decoder):
        result = decoder.decode("النار تحرق")
        for key in (
            "input", "mcd_analysis", "domain", "dal_madlul",
            "grounded_concepts", "claims", "rational_judgment",
            "correspondence", "fake_evidence_report", "conflicts",
            "certainty", "measures_created", "final_answer", "epistemic_status",
        ):
            assert key in result, f"Missing key: {key}"

    def test_epistemic_status_is_valid(self, decoder):
        result = decoder.decode("النار تحرق")
        assert result["epistemic_status"] in (
            "verified", "probable", "hypothesis", "suspended", "rejected"
        )

    def test_domain_is_epistemic(self, decoder):
        result = decoder.decode("النار تحرق")
        assert result["domain"]["judgment_type"] == "epistemic"

    def test_certainty_score_in_range(self, decoder):
        result = decoder.decode("النار تحرق")
        assert 0.0 <= result["certainty"]["score"] <= 1.0


class TestNabhaniDecoderKathabaStudentLesson:
    """كتب الطالب الدرس — general epistemic sentence."""

    def test_produces_output(self, decoder):
        result = decoder.decode("كتب الطالب الدرس")
        assert result["input"] == "كتب الطالب الدرس"

    def test_dal_madlul_has_entries(self, decoder):
        result = decoder.decode("كتب الطالب الدرس")
        assert len(result["dal_madlul"]) >= 1

    def test_grounded_concepts_per_word(self, decoder):
        result = decoder.decode("كتب الطالب الدرس")
        assert len(result["grounded_concepts"]) == 3  # كتب الطالب الدرس

    def test_no_shari_claim(self, decoder):
        result = decoder.decode("كتب الطالب الدرس")
        assert result["domain"]["status"] != "no_shari_ruling_available"


class TestNabhaniDecoderKidhbHarmVsHaram:
    """الكذب ضار vs الكذب حرام — key epistemic/shari distinction."""

    def test_kidhb_darr_is_epistemic(self, decoder):
        result = decoder.decode("الكذب ضار")
        assert result["domain"]["judgment_type"] == "epistemic"
        assert result["domain"]["status"] == "proceed_epistemic"
        assert result["domain"]["can_reason_without_revelation"] is True
        assert result["epistemic_status"] != "suspended" or result["rational_judgment"]["status"] != "rejected"

    def test_kidhb_haram_is_shari(self, decoder):
        result = decoder.decode("الكذب حرام")
        assert result["domain"]["judgment_type"] == "normative_shari"
        assert result["domain"]["status"] == "no_shari_ruling_available"
        assert result["epistemic_status"] == "suspended"

    def test_both_have_final_answer(self, decoder):
        r1 = decoder.decode("الكذب ضار")
        r2 = decoder.decode("الكذب حرام")
        assert r1["final_answer"]
        assert r2["final_answer"]
