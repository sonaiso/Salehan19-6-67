"""CFK Report generator — Markdown and JSON outputs."""
from __future__ import annotations

import json
import re
from mcd.cfk.cfk_pipeline import CognitiveFractalResult
from mcd.core.public_judgment import collapse_to_public_judgment, enforce_governed_output_contract


_JUDGMENT_ICONS = {
    "certificate": "✅",
    "hypothesis":  "🔶",
    "zero":        "❌",
}

_JUDGMENT_AR = {
    "certificate": "شهادة يقين",
    "hypothesis":  "فرضية — انتظار دليل/تعليق إجرائي",
    "zero":        "خطأ بنيوي — باقٍ معرفي",
}

# Characters that have special meaning in Markdown
_MD_SPECIAL = re.compile(r"([\\`*_{}[\]()#+\-.!|>])")


def _escape_md(text: str) -> str:
    """Escape Markdown special characters in user-supplied text."""
    return _MD_SPECIAL.sub(r"\\\1", text)


def _trunc(text: str, n: int) -> str:
    """Return at most *n* Unicode code-point characters from text.

    Python 3 strings are sequences of code points, so slicing is already
    safe for multi-byte encodings like Arabic Unicode. This helper makes the
    intent explicit and avoids reviewer confusion.
    """
    return text[:n]


def generate_markdown_report(result: CognitiveFractalResult) -> str:
    proof = result.proof
    public_judgment = collapse_to_public_judgment(proof.judgment)
    icon = _JUDGMENT_ICONS.get(public_judgment, "?")
    ar = _JUDGMENT_AR.get(public_judgment, public_judgment)
    # Escape user-supplied text before embedding in Markdown
    safe_text = _escape_md(result.text)

    lines = [
        f"# تقرير النواة الفراكتالية المعرفية (CFK)",
        f"",
        f"## النص المُحلَّل",
        f"> {safe_text}",
        f"",
        f"## الحكم النهائي",
        f"**{icon} {ar}**",
        f"",
        f"## المقاييس الرئيسية",
        f"| المقياس | القيمة |",
        f"|---------|--------|",
        f"| الثقة الإحصائية (GPT)       | {round(proof.statistical_confidence, 3)} |",
        f"| القوة اللغوية (العربية)     | {_escape_md(proof.linguistic_force)} |",
        f"| اليقين المعرفي (العقل)      | {round(proof.epistemic_certainty, 3)} |",
        f"| حالة الدليل                 | {_escape_md(proof.evidence_state)} |",
        f"| الباقي المعرفي              | {round(proof.cognitive_residual, 3)} |",
        f"| نوع الباقي                  | {_escape_md(proof.residual_type)} |",
        f"| إشارة التعلم                | {_escape_md(proof.learning_signal)} |",
        f"",
    ]
    if proof.judgment != public_judgment:
        lines.extend([
            f"_تحويل حوكمي:_ الحالة الداخلية `{proof.judgment}` → الحكم العام `{public_judgment}`.",
            "",
        ])

    # Conservation laws
    cons = proof.conservation
    lines += [
        f"## قوانين الحفظ",
        f"- **اجتاز الفحص:** {'نعم' if cons.passed else 'لا'}",
        f"- **درجة الحفظ:** {round(cons.conservation_score, 3)}",
    ]
    if cons.violations:
        lines.append("- **الانتهاكات:**")
        for v in cons.violations:
            lines.append(
                f"  - [{_escape_md(v.law)}] {_escape_md(v.description)} (خطورة: {_escape_md(v.severity)})"
            )
    lines.append("")

    # Notes from kernel
    if result.kernel.notes:
        lines.append("## ملاحظات النواة")
        for note in result.kernel.notes:
            lines.append(f"- {_escape_md(note)}")
        lines.append("")

    # Comparison table
    lines.append(result.table.to_markdown())
    lines.append("")

    # Reverse trace
    if proof.reverse_trace:
        lines += [
            "## مسار الرجوع (Reverse Trace)",
            " → ".join(proof.reverse_trace),
            "",
        ]

    return "\n".join(lines)


def generate_json_report(result: CognitiveFractalResult) -> str:
    return json.dumps(enforce_governed_output_contract(result.to_dict()), ensure_ascii=False, indent=2)
