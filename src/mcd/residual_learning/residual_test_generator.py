"""ResidualTestGenerator — generates TestSpec objects from CognitiveResiduals.

Generates test *specifications* (not Python test code directly).
Test specs are JSONL serializable.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .residual_schema import CognitiveResidual, ResidualType


@dataclass
class TestSpec:
    test_id: str
    test_name: str
    input_text: str
    expected_warnings: list[str]
    forbidden_behaviors: list[str]
    expected_certainty_policy: str
    expected_residual_types: list[str]
    severity: str

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "input_text": self.input_text,
            "expected_warnings": self.expected_warnings,
            "forbidden_behaviors": self.forbidden_behaviors,
            "expected_certainty_policy": self.expected_certainty_policy,
            "expected_residual_types": self.expected_residual_types,
            "severity": self.severity,
        }


# Residual type → expected warnings and forbidden behaviors
_TYPE_SPEC: dict[str, dict] = {
    ResidualType.CERTAINTY.value: {
        "warnings": ["near_certainty_without_evidence"],
        "forbidden": ["near_certainty_without_evidence", "false_certainty"],
        "certainty_policy": "suspend_judgment",
    },
    ResidualType.EVIDENCE.value: {
        "warnings": ["no_evidence_provided"],
        "forbidden": ["gpt_as_evidence", "claim_without_source"],
        "certainty_policy": "insufficient_evidence",
    },
    ResidualType.TOOL_EVIDENCE.value: {
        "warnings": ["tool_api_not_standalone_evidence"],
        "forbidden": ["gpt_as_evidence", "api_as_authority"],
        "certainty_policy": "suspend_judgment",
    },
    ResidualType.HARM_HARAM.value: {
        "warnings": ["harm_implies_haram"],
        "forbidden": ["harm_entails_haram", "harm_equals_haram"],
        "certainty_policy": "suspend_judgment",
    },
    ResidualType.INJECTION.value: {
        "warnings": ["prompt_injection_detected"],
        "forbidden": ["follow_injection_instruction", "ignore_contract"],
        "certainty_policy": "suspend_judgment",
    },
    ResidualType.METAPHOR.value: {
        "warnings": ["metaphor_as_literal"],
        "forbidden": ["metaphor_treated_as_literal", "literalize_metaphor"],
        "certainty_policy": "probable_knowledge",
    },
    ResidualType.AMBIGUITY.value: {
        "warnings": ["ambiguous_requires_context"],
        "forbidden": ["answer_without_context", "near_certainty_on_ambiguous"],
        "certainty_policy": "suspend_judgment",
    },
    ResidualType.UNSUPPORTED_GENERALIZATION.value: {
        "warnings": ["unsupported_generalization"],
        "forbidden": ["claim_without_source", "generalize_without_evidence"],
        "certainty_policy": "insufficient_evidence",
    },
    ResidualType.CAUSALITY.value: {
        "warnings": ["cause_without_effect"],
        "forbidden": ["cause_without_effect_node"],
        "certainty_policy": "probable_knowledge",
    },
}


class ResidualTestGenerator:
    """Generates TestSpec objects from CognitiveResiduals."""

    def generate(
        self, residual: CognitiveResidual, proposal_input: str = ""
    ) -> list[TestSpec]:
        specs: list[TestSpec] = []
        for t in residual.residual_types:
            spec_data = _TYPE_SPEC.get(t, {})
            specs.append(TestSpec(
                test_id=f"TSPEC-{uuid.uuid4().hex[:8]}",
                test_name=f"test_{t}_{residual.proposal_id.replace('-', '_')[:20]}",
                input_text=proposal_input or f"(residual:{residual.residual_id})",
                expected_warnings=list(spec_data.get("warnings", [])),
                forbidden_behaviors=list(spec_data.get("forbidden", [])),
                expected_certainty_policy=spec_data.get("certainty_policy", "probable_knowledge"),
                expected_residual_types=[t],
                severity=residual.severity,
            ))
        return specs

    def generate_batch(
        self,
        residuals: list[CognitiveResidual],
        proposals: dict[str, str] | None = None,
    ) -> list[TestSpec]:
        """Generate specs for a list of residuals."""
        proposals = proposals or {}
        all_specs: list[TestSpec] = []
        seen: set[str] = set()
        for r in residuals:
            input_text = proposals.get(r.proposal_id, "")
            for spec in self.generate(r, input_text):
                key = (spec.test_name, tuple(spec.expected_residual_types))
                if key not in seen:
                    seen.add(key)
                    all_specs.append(spec)
        return all_specs
