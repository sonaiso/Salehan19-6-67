"""MurabReport — generates human-readable and dict reports for I'rab analysis."""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit


class MurabReport:
    """Generates I'rab analysis reports in markdown and dict form."""

    def generate(self, units: list[MurabUnit], sentence: str) -> dict:
        return self.to_dict(units, sentence)

    def to_dict(self, units: list[MurabUnit], sentence: str) -> dict:
        return {
            "sentence": sentence,
            "token_count": len(units),
            "units": [u.to_dict() for u in units],
            "summary": self._summary(units),
        }

    def to_markdown(self, units: list[MurabUnit], sentence: str) -> str:
        lines = [
            f"# تحليل الإعراب",
            f"",
            f"**الجملة:** {sentence}",
            f"",
            f"| الرقم | الكلمة | نوعها | حالة الإعراب | العلامة | الدور النحوي | الدور الدلالي | الثقة |",
            f"|-------|--------|-------|--------------|---------|--------------|---------------|-------|",
        ]
        for i, u in enumerate(units, 1):
            lines.append(
                f"| {i} | {u.surface} | {u.word_type} | {u.irab_case} "
                f"| {u.irab_marker} | {u.syntactic_role} "
                f"| {u.semantic_role} | {u.certainty_policy} |"
            )

        lines.append("")
        lines.append("## ملاحظات")
        for u in units:
            for w in u.warnings:
                lines.append(f"- [{u.surface}]: {w}")

        return "\n".join(lines)

    def _summary(self, units: list[MurabUnit]) -> dict:
        cases: dict[str, int] = {}
        for u in units:
            cases[u.irab_case] = cases.get(u.irab_case, 0) + 1
        return {
            "case_distribution": cases,
            "total_warnings": sum(len(u.warnings) for u in units),
        }
