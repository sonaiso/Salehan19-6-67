"""Report — generate human-readable text report from GroundedReasoningFrame."""
from __future__ import annotations

from mcd.grounding.grounded_frame import GroundedReasoningFrame


def generate_report(frame: GroundedReasoningFrame) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("تقرير الإطار المعرفي المُؤسَّس (GLCFL)")
    lines.append("=" * 60)
    lines.append(f"النص المُدخَل:    {frame.input_text}")
    lines.append(f"الحالة النهائية:  {frame.final_status}")
    lines.append(f"الإجابة النهائية: {frame.final_answer or '—'}")
    lines.append(f"مؤشر اليقين:     {frame.certainty_summary:.3f}")
    lines.append("")

    if frame.grounded_lexemes:
        lines.append(f"المفردات المُؤسَّسة ({len(frame.grounded_lexemes)}):")
        for lex in frame.grounded_lexemes:
            status = lex.get("grounding_status", "?") if isinstance(lex, dict) else getattr(lex, "grounding_status", "?")
            surface = lex.get("surface", "?") if isinstance(lex, dict) else getattr(lex, "surface", "?")
            certainty = lex.get("certainty", 0.0) if isinstance(lex, dict) else getattr(lex, "certainty", 0.0)
            lines.append(f"  • {surface} → {status} (يقين: {certainty:.2f})")
        lines.append("")

    if frame.role_frames:
        lines.append(f"إطارات الأدوار ({len(frame.role_frames)}):")
        for rf in frame.role_frames:
            action = rf.get("action", "?") if isinstance(rf, dict) else getattr(rf, "action", "?")
            agent = rf.get("agent", "?") if isinstance(rf, dict) else getattr(rf, "agent", "?")
            patient = rf.get("patient", "?") if isinstance(rf, dict) else getattr(rf, "patient", "?")
            lines.append(f"  • الفعل={action} | الفاعل={agent} | المفعول={patient}")
        lines.append("")

    if frame.nisbah_frames:
        lines.append(f"إطارات النسبة ({len(frame.nisbah_frames)}):")
        for nf in frame.nisbah_frames:
            src = nf.get("source", "?") if isinstance(nf, dict) else getattr(nf, "source", "?")
            rel = nf.get("relation_type", "?") if isinstance(nf, dict) else getattr(nf, "relation_type", "?")
            tgt = nf.get("target", "?") if isinstance(nf, dict) else getattr(nf, "target", "?")
            lines.append(f"  • {src} —[{rel}]→ {tgt}")
        lines.append("")

    if frame.value_frames:
        lines.append(f"إطارات القيم ({len(frame.value_frames)}):")
        for vf in frame.value_frames:
            value = vf.get("value", "?") if isinstance(vf, dict) else getattr(vf, "value", "?")
            vtype = vf.get("value_type", "?") if isinstance(vf, dict) else getattr(vf, "value_type", "?")
            jtype = vf.get("judgment_type", "?") if isinstance(vf, dict) else getattr(vf, "judgment_type", "?")
            lines.append(f"  • {value}: نوع={vtype}, حكم={jtype}")
        lines.append("")

    if frame.civilization_frames:
        lines.append(f"إطارات الحضارة/المدنية ({len(frame.civilization_frames)}):")
        for cf in frame.civilization_frames:
            item = cf.get("item", "?") if isinstance(cf, dict) else getattr(cf, "item", "?")
            is_civ = cf.get("is_civilization", False) if isinstance(cf, dict) else getattr(cf, "is_civilization", False)
            is_civ_str = cf.get("is_civility", False) if isinstance(cf, dict) else getattr(cf, "is_civility", False)
            lines.append(f"  • {item}: حضارة={is_civ}, مدنية={is_civ_str}")
        lines.append("")

    if frame.warnings:
        lines.append(f"تحذيرات ({len(frame.warnings)}):")
        for w in frame.warnings:
            lines.append(f"  ⚠ {w}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)
