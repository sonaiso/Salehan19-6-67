"""CFK Pipeline — full orchestration of the Cognitive Fractal Kernel.

Pipeline:
    GPT Output
    → S(x): Statistical Transform
    → A(x): Arabic Semantic Transform
    → E(x): Epistemic Transform
    → K:    Fractal Kernel (unification)
    → ConservationLaw checks
    → ProofObject (Certificate | Hypothesis | Suspend | Zero)
    → ComparisonTable
    → CognitiveFractalResidual (learning signal)

Usage:
    pipeline = CognitiveFractalPipeline()
    result = pipeline.run(text, proposal_dict=..., evidence_refs=...)
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform
from mcd.cfk.fractal_kernel import FractalKernel, KernelResult
from mcd.cfk.conservation_law import ConservationLawChecker, ConservationCheckResult
from mcd.cfk.proof_object import ProofObject, ProofObjectBuilder
from mcd.cfk.cfk_comparison_table import ComparisonTable, ComparisonTableBuilder


@dataclass
class CognitiveFractalResult:
    """The complete output of one pipeline run."""

    run_id: str
    text: str
    kernel: KernelResult
    conservation_results: list[ConservationCheckResult]
    proof: ProofObject
    table: ComparisonTable

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "text": self.text,
            "kernel": self.kernel.to_dict(),
            "conservation": [c.to_dict() for c in self.conservation_results],
            "proof": self.proof.to_dict(),
            "table": self.table.to_dict(),
        }

    def summary(self) -> str:
        lines = [
            f"النص: {self.text[:70]}",
            f"الحكم: {self.proof.judgment}",
            f"الثقة الإحصائية: {round(self.proof.statistical_confidence, 3)}",
            f"القوة اللغوية: {self.proof.linguistic_force}",
            f"اليقين المعرفي: {round(self.proof.epistemic_certainty, 3)}",
            f"الدليل: {self.proof.evidence_state}",
            f"الباقي المعرفي: {round(self.proof.cognitive_residual, 3)} ({self.proof.residual_type})",
            f"إشارة التعلم: {self.proof.learning_signal}",
        ]
        if not self.proof.conservation.passed:
            lines.append(
                f"تحذير: {len(self.proof.conservation.violations)} انتهاك لقوانين الحفظ"
            )
        return "\n".join(lines)


class CognitiveFractalPipeline:
    """Orchestrates the full CFK pipeline."""

    def __init__(self) -> None:
        self._stat  = StatisticalTransform()
        self._arab  = ArabicSemanticTransform()
        self._epis  = EpistemicTransform()
        self._kernel = FractalKernel()
        self._conservation = ConservationLawChecker()
        self._proof_builder = ProofObjectBuilder()
        self._table_builder = ComparisonTableBuilder()

    def run(
        self,
        text: str,
        proposal_dict: dict | None = None,
        evidence_refs: list[str] | None = None,
        evidence_types: list[str] | None = None,
    ) -> CognitiveFractalResult:
        """Run the full pipeline on a text claim.

        Args:
            text:          The Arabic claim / sentence to analyse.
            proposal_dict: Optional GPT proposal dict (from GPTProposal.to_dict()).
                           If None, a default proposal is constructed from the text.
            evidence_refs: Optional list of evidence references.
            evidence_types: Optional list of evidence types.
        """
        evidence_refs  = evidence_refs or []
        evidence_types = evidence_types or []

        # ------------------------------------------------------------------ #
        # Step 1: Build proposal dict for statistical transform
        # ------------------------------------------------------------------ #
        if proposal_dict is None:
            proposal_dict = {
                "proposal_id":      f"auto-{uuid.uuid4().hex[:8]}",
                "gpt_output":       text,
                "input_text":       text,
                "proposal_type":    "answer",
                "claimed_evidence": evidence_refs,
                "claimed_certainty": None,
            }
        # Merge in any provided evidence_refs
        if evidence_refs and not proposal_dict.get("claimed_evidence"):
            proposal_dict["claimed_evidence"] = evidence_refs

        # ------------------------------------------------------------------ #
        # Step 2: Apply three transforms
        # ------------------------------------------------------------------ #
        stat_proj = self._stat.transform(proposal_dict)
        arab_proj = self._arab.transform(text)
        epis_proj = self._epis.transform(
            text,
            statistical_confidence=stat_proj.comparable_score,
            evidence_refs=evidence_refs,
            evidence_types=evidence_types,
            linguistic_force=arab_proj.unit.C.linguistic_force,
            source_text=text,
        )

        # ------------------------------------------------------------------ #
        # Step 3: Apply fractal kernel K
        # ------------------------------------------------------------------ #
        kernel = self._kernel.apply(text, stat_proj, arab_proj, epis_proj)

        # ------------------------------------------------------------------ #
        # Step 4: Check conservation laws on all three units
        # ------------------------------------------------------------------ #
        conservation_results = [
            self._conservation.check(stat_proj.unit),
            self._conservation.check(arab_proj.unit),
            self._conservation.check(epis_proj.unit),
        ]

        # ------------------------------------------------------------------ #
        # Step 5: Build ProofObject
        # ------------------------------------------------------------------ #
        proof = self._proof_builder.build(kernel, conservation_results)

        # ------------------------------------------------------------------ #
        # Step 6: Build ComparisonTable
        # ------------------------------------------------------------------ #
        table = self._table_builder.build(kernel, proof)

        return CognitiveFractalResult(
            run_id=f"CFR-{uuid.uuid4().hex[:10]}",
            text=text,
            kernel=kernel,
            conservation_results=conservation_results,
            proof=proof,
            table=table,
        )
