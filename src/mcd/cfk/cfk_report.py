"""CFK Report generator — Markdown and JSON outputs."""
from __future__ import annotations

import json
from mcd.cfk.cfk_pipeline import CognitiveFractalResult


_JUDGMENT_ICONS = {
    "certificate": "✅",
    "hypothesis":  "🔶",
    "suspend":     "⏸️",
    "zero":        "❌",
}

_JUDGMENT_AR = {
    "certificate": "شهادة يقين",
    "hypothesis":  "فرضية — انتظار دليل",
    "suspend":     "تعليق — دليل ناقص",
    "zero":        "خطأ بنيوي — باقٍ معرفي",
}


def generate_markdown_report(result: CognitiveFractalResult) -> str:
    proof = result.proof
    icon  = _JUDGMENT_ICONS.get(proof.judgment, "?")
    ar    = _JUDGMENT_AR.get(proof.judgment, proof.judgment)

    lines = [
        f"# تقرير النواة الفراكتالية المعرفية (CFK)",
        f"",
        f"## النص المُحلَّل",
        f"> {result.text}",
        f"",
        f"## الحكم النهائي",
        f"**{icon} {ar}**",
        f"",
        f"## المقاييس الرئيسية",
        f"| المقياس | القيمة |",
        f"|---------|--------|",
        f"| الثقة الإحصائية (GPT)       | {round(proof.statistical_confidence, 3)} |",
        f"| القوة اللغوية (العربية)     | {proof.linguistic_force} |",
        f"| اليقين المعرفي (العقل)      | {round(proof.epistemic_certainty, 3)} |",
        f"| حالة الدليل                 | {proof.evidence_state} |",
        f"| الباقي المعرفي              | {round(proof.cognitive_residual, 3)} |",
        f"| نوع الباقي                  | {proof.residual_type} |",
        f"| إشارة التعلم                | {proof.learning_signal} |",
        f"",
    ]

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
            lines.append(f"  - [{v.law}] {v.description} (خطورة: {v.severity})")
    lines.append("")

    # Notes from kernel
    if result.kernel.notes:
        lines.append("## ملاحظات النواة")
        for note in result.kernel.notes:
            lines.append(f"- {note}")
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
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
