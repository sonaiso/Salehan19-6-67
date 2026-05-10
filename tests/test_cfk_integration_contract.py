"""Tests for Phase 8.1 — CFKIntegrationContract."""
from __future__ import annotations

import pytest

from mcd.cfk.cfk_integration_contract import (
    CFKIntegrationContract,
    ContractValidator,
    ContractViolation,
    STATISTICAL_TRANSFORM_CONTRACT,
    ARABIC_SEMANTIC_TRANSFORM_CONTRACT,
    MABNI_CONTRACT,
    MURAB_CONTRACT,
    EPISTEMIC_TRANSFORM_CONTRACT,
    PROOF_OBJECT_BUILDER_CONTRACT,
    ALL_CONTRACTS,
    CONTRACTS_BY_LAYER,
)
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform


# ---------------------------------------------------------------------------
# Contract definitions
# ---------------------------------------------------------------------------

class TestContractDefinitions:
    """Verify that all built-in contracts have the expected permissions."""

    def test_statistical_cannot_create_evidence(self):
        assert STATISTICAL_TRANSFORM_CONTRACT.can_create_evidence is False

    def test_statistical_cannot_raise_epistemic_certainty(self):
        assert STATISTICAL_TRANSFORM_CONTRACT.can_raise_epistemic_certainty is False

    def test_statistical_cannot_issue_certificate(self):
        assert STATISTICAL_TRANSFORM_CONTRACT.can_issue_certificate is False

    def test_arabic_cannot_create_evidence(self):
        assert ARABIC_SEMANTIC_TRANSFORM_CONTRACT.can_create_evidence is False

    def test_arabic_cannot_raise_epistemic_certainty(self):
        assert ARABIC_SEMANTIC_TRANSFORM_CONTRACT.can_raise_epistemic_certainty is False

    def test_arabic_can_set_linguistic_force(self):
        assert ARABIC_SEMANTIC_TRANSFORM_CONTRACT.can_set_linguistic_force is True

    def test_arabic_cannot_issue_certificate(self):
        assert ARABIC_SEMANTIC_TRANSFORM_CONTRACT.can_issue_certificate is False

    def test_mabni_cannot_create_evidence(self):
        assert MABNI_CONTRACT.can_create_evidence is False

    def test_mabni_can_change_judgment_operation(self):
        assert MABNI_CONTRACT.can_change_judgment_operation is True

    def test_mabni_cannot_raise_factual_certainty(self):
        assert MABNI_CONTRACT.can_raise_factual_certainty is False

    def test_murab_can_raise_syntactic_certainty(self):
        assert MURAB_CONTRACT.can_raise_syntactic_certainty is True

    def test_murab_cannot_raise_factual_certainty(self):
        assert MURAB_CONTRACT.can_raise_factual_certainty is False

    def test_murab_cannot_raise_epistemic_certainty(self):
        assert MURAB_CONTRACT.can_raise_epistemic_certainty is False

    def test_epistemic_can_evaluate_evidence(self):
        assert EPISTEMIC_TRANSFORM_CONTRACT.can_evaluate_evidence is True

    def test_epistemic_can_raise_epistemic_certainty(self):
        assert EPISTEMIC_TRANSFORM_CONTRACT.can_raise_epistemic_certainty is True

    def test_epistemic_cannot_issue_certificate(self):
        assert EPISTEMIC_TRANSFORM_CONTRACT.can_issue_certificate is False

    def test_proof_builder_can_issue_certificate(self):
        assert PROOF_OBJECT_BUILDER_CONTRACT.can_issue_certificate is True

    def test_proof_builder_cannot_create_evidence(self):
        assert PROOF_OBJECT_BUILDER_CONTRACT.can_create_evidence is False

    def test_all_contracts_count(self):
        assert len(ALL_CONTRACTS) == 6

    def test_contracts_by_layer_lookup(self):
        assert "statistical_transform" in CONTRACTS_BY_LAYER
        assert "arabic_semantic_transform" in CONTRACTS_BY_LAYER
        assert "epistemic_transform" in CONTRACTS_BY_LAYER
        assert "proof_object_builder" in CONTRACTS_BY_LAYER

    def test_contract_to_dict(self):
        d = STATISTICAL_TRANSFORM_CONTRACT.to_dict()
        assert d["source_layer"] == "statistical_transform"
        assert d["can_create_evidence"] is False
        assert d["can_issue_certificate"] is False


# ---------------------------------------------------------------------------
# ContractValidator — StatisticalTransform
# ---------------------------------------------------------------------------

class TestContractValidatorStatistical:
    def setup_method(self):
        self.transform = StatisticalTransform()
        self.validator = ContractValidator()

    def _proposal(self, text="النار حارة", claimed=None, evidence=None):
        return {
            "proposal_id": "P-test",
            "gpt_output": text,
            "input_text": text,
            "proposal_type": "answer",
            "claimed_certainty": claimed,
            "claimed_evidence": evidence or [],
        }

    def test_valid_statistical_projection(self):
        proj = self.transform.transform(self._proposal())
        result = self.validator.validate_statistical_projection(proj)
        assert result.passed, result.violations

    def test_statistical_epistemic_must_be_zero(self):
        proj = self.transform.transform(self._proposal(claimed="near_certainty"))
        # Manually tamper: simulate a broken transform that sets epistemic_certainty
        proj.unit.C.epistemic_certainty = 0.9
        result = self.validator.validate_statistical_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "no_epistemic_certainty" in rules

    def test_statistical_no_proof(self):
        proj = self.transform.transform(self._proposal())
        # Manually tamper
        proj.unit.P.produces_proof = True
        result = self.validator.validate_statistical_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "no_proof" in rules


# ---------------------------------------------------------------------------
# ContractValidator — ArabicSemanticTransform
# ---------------------------------------------------------------------------

class TestContractValidatorArabic:
    def setup_method(self):
        self.transform = ArabicSemanticTransform()
        self.validator = ContractValidator()

    def test_valid_arabic_projection(self):
        proj = self.transform.transform("زيد كاتب")
        result = self.validator.validate_arabic_projection(proj)
        assert result.passed, result.violations

    def test_arabic_cannot_set_epistemic_certainty(self):
        proj = self.transform.transform("إن زيداً كاتب")
        # Tamper
        proj.unit.C.epistemic_certainty = 0.8
        result = self.validator.validate_arabic_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "no_epistemic_certainty" in rules

    def test_arabic_evidence_state_must_be_missing(self):
        proj = self.transform.transform("زيد كاتب")
        # Tamper
        proj.unit.E.evidence_state = "present"
        result = self.validator.validate_arabic_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "no_evidence" in rules

    def test_arabic_fallback_score_cap_enforced(self):
        proj = self.transform.transform("زيد كاتب")
        # Simulate fallback with inflated score
        proj.unit.metadata["murab_fallback"] = True
        proj.comparable_score = 0.80
        result = self.validator.validate_arabic_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "fallback_score_cap" in rules

    def test_arabic_no_fallback_no_cap(self):
        proj = self.transform.transform("زيد كاتب")
        # murab_fallback=False, high score should be fine in principle
        proj.unit.metadata["murab_fallback"] = False
        proj.unit.metadata["mabni_fallback"] = False
        proj.comparable_score = 0.80
        proj.unit.E.evidence_state = "missing"
        result = self.validator.validate_arabic_projection(proj)
        # Only check that fallback_score_cap is NOT in violations
        rules = [v.rule for v in result.violations]
        assert "fallback_score_cap" not in rules


# ---------------------------------------------------------------------------
# ContractValidator — EpistemicTransform
# ---------------------------------------------------------------------------

class TestContractValidatorEpistemic:
    def setup_method(self):
        self.transform = EpistemicTransform()
        self.validator = ContractValidator()

    def test_valid_epistemic_missing_evidence(self):
        proj = self.transform.transform("test")
        result = self.validator.validate_epistemic_projection(proj)
        assert result.passed, result.violations

    def test_valid_epistemic_with_evidence(self):
        proj = self.transform.transform(
            "النار حارة",
            statistical_confidence=0.9,
            evidence_refs=["e1", "e2"],
        )
        result = self.validator.validate_epistemic_projection(proj)
        assert result.passed, result.violations

    def test_epistemic_gate_missing_evidence(self):
        proj = self.transform.transform("test", statistical_confidence=0.9)
        # Tamper: force high certainty without evidence
        proj.unit.C.epistemic_certainty = 0.85
        proj.unit.E.evidence_state = "missing"
        result = self.validator.validate_epistemic_projection(proj)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "evidence_gate" in rules


# ---------------------------------------------------------------------------
# Contract dataclass
# ---------------------------------------------------------------------------

class TestCFKIntegrationContractDataclass:
    def test_custom_contract(self):
        c = CFKIntegrationContract(
            source_layer="my_layer",
            projection_type="custom",
            can_create_evidence=False,
            can_issue_certificate=False,
        )
        assert c.source_layer == "my_layer"
        assert c.can_create_evidence is False

    def test_violation_to_dict(self):
        v = ContractViolation(
            source_layer="test",
            rule="test_rule",
            description="desc",
            severity="error",
        )
        d = v.to_dict()
        assert d["rule"] == "test_rule"
        assert d["severity"] == "error"
