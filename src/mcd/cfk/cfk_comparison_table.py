"""Comparison Table — Section 16 of the Fractal Proof.

Generates a structured table comparing the three coordinate systems
(GPT/Statistical, Arabic/Semantic, Epistemic) for a given claim.

Example (from Section 16):
| البعد       | نتيجة GPT     | نتيجة العربية     | نتيجة العقل |
|-------------|---------------|-------------------|-------------|
| نوع الجملة  | محتمل خبر     | خبر مؤكد           | دعوى        |
| القوة       | عالية لغويًا  | توكيد              | لا دليل     |
| الدليل      | غير موجود     | غير مذكور          | مطلوب       |
| اليقين      | إحصائي        | تداولي             | معلق        |
| الحكم       | plausible     | emphasized claim   | Hypothesis  |
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.cfk.fractal_kernel import KernelResult
from mcd.cfk.proof_object import ProofObject
from mcd.core.public_judgment import collapse_to_public_judgment


# ---------------------------------------------------------------------------
# Row dataclass
# ---------------------------------------------------------------------------

@dataclass
class ComparisonRow:
    dimension: str           # e.g. "نوع الجملة"
    statistical_value: str   # GPT result
    arabic_value: str        # Arabic result
    epistemic_value: str     # Epistemic result

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "statistical": self.statistical_value,
            "arabic": self.arabic_value,
            "epistemic": self.epistemic_value,
        }


@dataclass
class ComparisonTable:
    text: str
    rows: list[ComparisonRow] = field(default_factory=list)
    kernel_judgment: str = "hypothesis"

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "kernel_judgment": self.kernel_judgment,
            "rows": [r.to_dict() for r in self.rows],
        }

    def to_markdown(self) -> str:
        lines = [
            f"## جدول المقارنة: {self.text[:60]}",
            "",
            "| البعد | نتيجة GPT (إحصائي) | نتيجة العربية | نتيجة العقل |",
            "|-------|---------------------|---------------|-------------|",
        ]
        for row in self.rows:
            lines.append(
                f"| {row.dimension} | {row.statistical_value} | {row.arabic_value} | {row.epistemic_value} |"
            )
        lines.append("")
        lines.append(f"**الحكم النهائي (النواة):** `{self.kernel_judgment}`")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class ComparisonTableBuilder:
    """Builds a ComparisonTable from a KernelResult and ProofObject."""

    def build(self, kernel: KernelResult, proof: ProofObject) -> ComparisonTable:
        stat_u  = kernel.statistical.unit
        arab_u  = kernel.arabic.unit
        epis_u  = kernel.epistemic.unit

        # --- Sentence type ---
        stat_sent   = f"محتمل ({stat_u.N.unit_type})"
        arab_sent   = self._arabic_sentence_type(arab_u.C.linguistic_force)
        epis_sent   = "دعوى"

        # --- Force / strength ---
        stat_force  = f"ثقة إحصائية={round(stat_u.V.statistical_weight, 2)}"
        arab_force  = arab_u.C.linguistic_force
        epis_force  = (
            "لا دليل بعد" if epis_u.E.evidence_state == "missing"
            else f"دليل={epis_u.E.evidence_state}"
        )

        # --- Evidence ---
        stat_ev     = "غير موجود"
        arab_ev     = "غير مذكور"
        epis_ev     = (
            "مطلوب" if epis_u.E.evidence_state == "missing"
            else ("جزئي" if epis_u.E.evidence_state == "partial" else "موجود")
        )

        # --- Certainty ---
        stat_cert   = f"إحصائي ({round(stat_u.C.statistical_confidence, 2)})"
        arab_cert   = f"تداولي ({arab_u.C.linguistic_force})"
        public_judgment = collapse_to_public_judgment(proof.judgment)
        epis_cert   = (
            "معلق" if (proof.internal_state == "suspended" or proof.judgment == "zero")
            else f"{epis_u.C.certainty_level}"
        )

        # --- Judgment ---
        stat_judg   = "plausible"
        arab_judg   = self._arabic_judgment_label(arab_u.C.linguistic_force)
        epis_judg   = public_judgment

        rows = [
            ComparisonRow("نوع الجملة",  stat_sent,  arab_sent,  epis_sent),
            ComparisonRow("القوة",        stat_force, arab_force, epis_force),
            ComparisonRow("الدليل",       stat_ev,    arab_ev,    epis_ev),
            ComparisonRow("اليقين",       stat_cert,  arab_cert,  epis_cert),
            ComparisonRow("الحكم",        stat_judg,  arab_judg,  epis_judg),
        ]

        return ComparisonTable(
            text=kernel.text,
            rows=rows,
            kernel_judgment=public_judgment,
        )

    @staticmethod
    def _arabic_sentence_type(linguistic_force: str) -> str:
        mapping = {
            "emphasis":    "خبر مؤكد",
            "negation":    "نفي",
            "condition":   "شرط",
            "restriction": "قصر",
            "universal":   "تعميم كلي",
            "neutral":     "خبر",
        }
        return mapping.get(linguistic_force, "جملة")

    @staticmethod
    def _arabic_judgment_label(linguistic_force: str) -> str:
        mapping = {
            "emphasis":    "دعوى مؤكدة",
            "negation":    "نفي",
            "condition":   "شرط",
            "restriction": "قصر",
            "universal":   "تعميم",
            "neutral":     "خبر عادي",
        }
        return mapping.get(linguistic_force, "دعوى")
