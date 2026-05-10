"""MabniReport — generates reports from MabniUnfoldResult."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MabniReport:
    result_dict: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_type": "mabni_analysis",
            "text": self.result_dict.get("text", ""),
            "speech_act": self.result_dict.get("speech_act", {}),
            "key_findings": self._key_findings(),
            "warnings": self.warnings or self.result_dict.get("warnings", []),
        }

    def _key_findings(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        sa = self.result_dict.get("speech_act", {})
        if sa.get("speech_act"):
            findings.append({"category": "speech_act", "value": sa.get("speech_act")})

        for key in ("ma_result", "man_result", "in_result", "la_result"):
            res = self.result_dict.get(key, {})
            if res.get("resolved_type"):
                findings.append({"category": key, "resolved_type": res.get("resolved_type")})

        cond = self.result_dict.get("conditional_result", {})
        if cond.get("is_conditional"):
            findings.append({
                "category": "conditional",
                "particle": cond.get("conditional_particle"),
                "judgment_suspended": cond.get("judgment_suspended"),
            })

        cf = self.result_dict.get("counterfactual_result", {})
        if cf.get("is_counterfactual"):
            findings.append({
                "category": "counterfactual",
                "particle": cf.get("counterfactual_particle"),
            })

        qasr = self.result_dict.get("qasr_result", {})
        if qasr.get("qasr_type"):
            findings.append({
                "category": "qasr",
                "qasr_type": qasr.get("qasr_type"),
                "is_evidence": qasr.get("is_evidence", False),
            })

        exc = self.result_dict.get("exception_result", {})
        if exc.get("particle"):
            findings.append({
                "category": "exception",
                "particle": exc.get("particle"),
                "scope_modified": exc.get("scope_modified"),
            })

        emp = self.result_dict.get("emphasis_result", {})
        if emp.get("has_emphasis"):
            findings.append({
                "category": "emphasis",
                "markers": emp.get("emphasis_markers"),
                "creates_evidence": emp.get("creates_evidence", False),
            })

        return findings

    def generate(self) -> str:
        """Generate a markdown report."""
        d = self.to_dict()
        text = d.get("text", "")
        speech_act = d.get("speech_act", {})
        findings = d.get("key_findings", [])
        warns = d.get("warnings", [])

        lines = [
            "# Mabni Analysis Report",
            "",
            f"**Text:** {text}",
            "",
            "## Speech Act",
            f"- Type: `{speech_act.get('speech_act', 'unknown')}`",
            f"- Is assertion: `{speech_act.get('is_assertion', 'unknown')}`",
            f"- Establishes reality: `{speech_act.get('establishes_reality', 'unknown')}`",
            "",
            "## Key Findings",
            "",
        ]

        if findings:
            for f in findings:
                cat = f.pop("category", "unknown")
                parts = ", ".join(f"{k}: {v}" for k, v in f.items())
                lines.append(f"- **{cat}**: {parts}")
        else:
            lines.append("- No special mabni operators detected.")

        lines += ["", "## Warnings", ""]
        if warns:
            for w in warns:
                lines.append(f"- {w}")
        else:
            lines.append("- None")

        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
