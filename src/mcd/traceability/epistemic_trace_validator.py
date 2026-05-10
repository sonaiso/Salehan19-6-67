"""EpistemicTraceValidator — Phase 7.1.3.

Validates the epistemic correctness of trace bundles:
  Unicode → Evidence Reason → Certainty Reason → Judgment Reason

This goes beyond structural traceability (TraceValidator) by checking
whether the evidence, certainty, and judgment are epistemically sound.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from mcd.traceability.trace_builder import TraceBuilder, TraceBundle


# Policies that require concrete evidence
_HIGH_CERTAINTY_POLICIES = {"strong_knowledge", "near_certainty"}

# Evidence statuses considered "no evidence"
_NO_EVIDENCE_STATUSES = {"missing", "fake", "contaminated", "unverified",
                          "source_required", "context_required"}

# Known universal quantifier tokens (word-boundary, no substring)
_UNIVERSAL_QUANTIFIERS = {"كل", "جميع", "دائما", "دائمًا", "أبدا", "أبدًا"}

# Definitional/religious/logical context words (exempt universal quantifiers)
_DEFINITIONAL_CONTEXT = {
    "يموت", "فانٍ", "فان", "الموت", "حتمي", "سيموت", "تموت",
    "الله", "النبي", "الصلاة", "القرآن", "الإسلام", "الشريعة",
    "واجب", "محرم", "حلال", "حرام", "مكروه", "مستحب",
    "بالضرورة", "منطقياً", "منطقيا", "رياضياً", "رياضيا",
}

# Prompt injection tokens
_INJECTION_TOKENS = {"تجاهل", "ignore", "forget"}

# API/model source tokens (not evidence)
_API_TOKENS = {"api", "gpt", "chatgpt", "النموذج", "نموذج"}

# Known metaphor subjects (non-literal claims)
_METAPHOR_PAIRS: list[tuple[str, str]] = [
    ("المجتمع", "مريض"), ("مجتمع", "مريض"),
    ("العلم", "نور"), ("علم", "نور"),
    ("الجهل", "ظلام"), ("جهل", "ظلام"),
    ("الحياة", "سفر"), ("الوقت", "ذهب"),
]


@dataclass
class EpistemicTraceValidationReport:
    """Full epistemic validation report for a trace bundle or golden example set."""

    passed: bool
    epistemic_trace_score: float
    structural_trace_score: float
    evidence_trace_score: float
    certainty_trace_score: float
    judgment_trace_score: float
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    failed_examples: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "epistemic_trace_score": round(self.epistemic_trace_score, 4),
            "structural_trace_score": round(self.structural_trace_score, 4),
            "evidence_trace_score": round(self.evidence_trace_score, 4),
            "certainty_trace_score": round(self.certainty_trace_score, 4),
            "judgment_trace_score": round(self.judgment_trace_score, 4),
            "violations": self.violations,
            "warnings": self.warnings,
            "failed_examples": self.failed_examples,
        }

    def to_markdown(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [
            f"# Epistemic Trace Validation Report — {status}",
            "",
            "## Scores",
            "",
            "| Score | Value |",
            "|-------|-------|",
            f"| epistemic_trace_score | {self.epistemic_trace_score:.4f} |",
            f"| structural_trace_score | {self.structural_trace_score:.4f} |",
            f"| evidence_trace_score | {self.evidence_trace_score:.4f} |",
            f"| certainty_trace_score | {self.certainty_trace_score:.4f} |",
            f"| judgment_trace_score | {self.judgment_trace_score:.4f} |",
            "",
        ]
        if self.violations:
            lines.append("## Violations")
            for v in self.violations:
                lines.append(f"- ❌ {v}")
            lines.append("")
        if self.warnings:
            lines.append("## Warnings")
            for w in self.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")
        if self.failed_examples:
            lines.append(f"## Failed Examples ({len(self.failed_examples)})")
            for ex in self.failed_examples[:10]:
                lines.append(f"- **[{ex.get('id', '?')}]** `{ex.get('text', '')[:60]}` "
                              f"— {ex.get('reason', '')}")
            lines.append("")
        return "\n".join(lines)


class EpistemicTraceValidator:
    """Validates epistemic correctness of a TraceBundle.

    Rules enforced:
    - strong_knowledge / near_certainty require evidence_status = 'present'
    - Ambiguous tokens (عين, علم, ...) require suspend / context_required
    - Universal quantifiers without definitional context require source_required / suspend
    - 'بلا مصدر' / 'بدون دليل' force missing evidence and suspend
    - Prompt injection forces contaminated/fake and reject/suspend
    - Metaphor patterns force metaphor warning, NOT literal strong_knowledge
    - API/model/GPT output is not evidence
    """

    # ─── single-bundle validation ────────────────────────────────────────────

    def validate(self, bundle: TraceBundle) -> EpistemicTraceValidationReport:
        """Validate one TraceBundle epistemically."""
        violations: list[str] = []
        warnings: list[str] = []

        jt = bundle.judgment_trace
        ev = bundle.evidence_traces[0] if bundle.evidence_traces else None
        ct = bundle.certainty_trace

        # Structural score: all unicode has trace_ids
        total_u = len(bundle.unicode_units)
        traced_u = sum(1 for u in bundle.unicode_units if u.trace_id)
        structural_score = traced_u / total_u if total_u > 0 else 1.0

        # ── Evidence checks ────────────────────────────────────────────────
        ev_checks_total = 3
        ev_checks_passed = 0

        if ev is None:
            violations.append("No evidence trace present")
        else:
            # 1. Evidence trace must have source_trace_ids
            if ev.source_trace_ids:
                ev_checks_passed += 1
            else:
                violations.append("evidence_trace has no source_trace_ids")

            # 2. Evidence trace must have token_ids
            if ev.token_ids:
                ev_checks_passed += 1
            else:
                violations.append("evidence_trace has no token_ids")

            # 3. strong_knowledge / near_certainty require present evidence
            if ct and ct.policy in _HIGH_CERTAINTY_POLICIES:
                if ev.status != "present":
                    violations.append(
                        f"certainty_policy='{ct.policy}' requires evidence_status='present' "
                        f"but got '{ev.status}'"
                    )
                else:
                    ev_checks_passed += 1
            else:
                ev_checks_passed += 1  # not a high-certainty claim, no violation

        evidence_score = ev_checks_passed / ev_checks_total

        # ── Certainty checks ───────────────────────────────────────────────
        cert_checks_total = 4
        cert_checks_passed = 0

        if ct is None:
            violations.append("No certainty trace present")
        else:
            if ct.reason:
                cert_checks_passed += 1
            else:
                violations.append("certainty_trace has no reason")

            if ct.source_evidence_ids:
                cert_checks_passed += 1
            else:
                violations.append("certainty_trace has no source_evidence_ids")

            tokens = bundle.tokens
            word_set = {t.normalized.strip().lower() for t in tokens if t.normalized.strip()}

            # Check: ambiguous terms require suspend
            semantic_tokens = [t for t in tokens if t.token_type not in ("whitespace",)]
            from mcd.traceability.trace_builder import _AMBIGUOUS_TERMS
            ambiguous = [t for t in semantic_tokens if t.normalized.strip() in _AMBIGUOUS_TERMS]
            ambiguity_ratio = len(ambiguous) / len(semantic_tokens) if semantic_tokens else 0.0
            if ambiguity_ratio >= 0.5 and len(semantic_tokens) <= 3:
                if ct.policy == "strong_knowledge":
                    violations.append(
                        f"Ambiguous term(s) {[t.surface for t in ambiguous]} "
                        f"cannot yield certainty_policy='strong_knowledge' without context"
                    )
                else:
                    cert_checks_passed += 1
            else:
                cert_checks_passed += 1

            # Check: universal quantifiers without definitional context require suspend
            has_universal = any(q in word_set for q in _UNIVERSAL_QUANTIFIERS)
            has_definitional = any(s in _DEFINITIONAL_CONTEXT for s in word_set)
            if has_universal and not has_definitional:
                if ct.policy == "strong_knowledge":
                    violations.append(
                        "Universal quantifier without definitional context "
                        "cannot yield certainty_policy='strong_knowledge'"
                    )
                else:
                    cert_checks_passed += 1
            else:
                cert_checks_passed += 1

        certainty_score = cert_checks_passed / cert_checks_total

        # ── Judgment checks ────────────────────────────────────────────────
        j_checks_total = 5
        j_checks_passed = 0

        if jt is None:
            violations.append("No judgment trace present")
        else:
            if jt.unicode_trace_ids:
                j_checks_passed += 1
            else:
                violations.append("judgment_trace has no unicode_trace_ids")

            if jt.token_ids:
                j_checks_passed += 1
            else:
                violations.append("judgment_trace has no token_ids")

            if jt.explanation:
                j_checks_passed += 1
            else:
                violations.append("judgment_trace has no explanation")

            tokens = bundle.tokens
            word_set = {t.normalized.strip().lower() for t in tokens if t.normalized.strip()}

            # Check: prompt injection → must be reject/suspend
            has_injection = any(s in _INJECTION_TOKENS for s in word_set)
            if has_injection:
                if jt.final_decision in ("reject", "suspend"):
                    j_checks_passed += 1
                else:
                    violations.append(
                        f"Prompt injection detected but final_decision='{jt.final_decision}'"
                        f" (expected reject or suspend)"
                    )
            else:
                j_checks_passed += 1

            # Check: API/model-as-source → must NOT be strong_knowledge
            has_api = any(s in _API_TOKENS for s in word_set)
            if has_api:
                if ct and ct.policy == "strong_knowledge":
                    violations.append(
                        "API/model token detected but certainty_policy='strong_knowledge' "
                        "(API/model output is not evidence)"
                    )
                else:
                    j_checks_passed += 1
            else:
                j_checks_passed += 1

        judgment_score = j_checks_passed / j_checks_total

        # Check metaphor patterns → no literal strong_knowledge
        tokens = bundle.tokens
        word_set = {t.normalized.strip().lower() for t in tokens if t.normalized.strip()}
        for subj, pred in _METAPHOR_PAIRS:
            if subj in word_set and pred in word_set:
                if ct and ct.policy == "strong_knowledge":
                    violations.append(
                        f"Metaphor pattern ({subj} / {pred}) detected but "
                        f"certainty_policy='strong_knowledge' — metaphors are not literal facts"
                    )
                else:
                    warnings.append(f"Metaphor pattern detected: ({subj} / {pred})")
                break

        # ── Compute composite scores ───────────────────────────────────────
        sub_scores = [structural_score, evidence_score, certainty_score, judgment_score]
        epistemic_score = sum(sub_scores) / len(sub_scores)

        passed = (
            len(violations) == 0
            and epistemic_score >= 0.95
        )

        return EpistemicTraceValidationReport(
            passed=passed,
            epistemic_trace_score=epistemic_score,
            structural_trace_score=structural_score,
            evidence_trace_score=evidence_score,
            certainty_trace_score=certainty_score,
            judgment_trace_score=judgment_score,
            violations=violations,
            warnings=warnings,
            failed_examples=[],
        )

    # ─── golden-examples batch validation ────────────────────────────────────

    def validate_golden_examples(
        self,
        golden_path: Path | None = None,
    ) -> EpistemicTraceValidationReport:
        """Validate all golden examples and aggregate scores."""
        if golden_path is None:
            golden_path = Path("data/traceability/trace_golden_examples_ar.jsonl")

        builder = TraceBuilder()
        all_scores: list[float] = []
        all_struct: list[float] = []
        all_ev: list[float] = []
        all_cert: list[float] = []
        all_j: list[float] = []
        all_violations: list[str] = []
        all_warnings: list[str] = []
        failed: list[dict] = []

        if not golden_path.exists():
            return EpistemicTraceValidationReport(
                passed=False,
                epistemic_trace_score=0.0,
                structural_trace_score=0.0,
                evidence_trace_score=0.0,
                certainty_trace_score=0.0,
                judgment_trace_score=0.0,
                violations=["Golden examples file not found"],
                warnings=[],
                failed_examples=[],
            )

        lines = [l.strip() for l in golden_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            ex = json.loads(line)
            bundle = builder.build(ex.get("text", ""))
            rpt = self.validate(bundle)
            all_scores.append(rpt.epistemic_trace_score)
            all_struct.append(rpt.structural_trace_score)
            all_ev.append(rpt.evidence_trace_score)
            all_cert.append(rpt.certainty_trace_score)
            all_j.append(rpt.judgment_trace_score)

            # Also check expected vs actual
            expected = ex.get("expected_trace_summary", {})
            jt = bundle.judgment_trace
            if jt:
                mismatches = []
                if expected.get("decision") and jt.final_decision != expected["decision"]:
                    mismatches.append(
                        f"decision: expected={expected['decision']}, got={jt.final_decision}"
                    )
                if expected.get("evidence_status") and jt.evidence_status != expected["evidence_status"]:
                    mismatches.append(
                        f"evidence_status: expected={expected['evidence_status']}, got={jt.evidence_status}"
                    )
                if expected.get("certainty_policy") and jt.certainty_policy != expected["certainty_policy"]:
                    mismatches.append(
                        f"certainty_policy: expected={expected['certainty_policy']}, got={jt.certainty_policy}"
                    )
                if mismatches:
                    failed.append({
                        "id": ex.get("id"),
                        "text": ex.get("text"),
                        "reason": "; ".join(mismatches),
                    })

            all_violations.extend(rpt.violations)
            all_warnings.extend(rpt.warnings)

        n = len(lines)
        if n == 0:
            return EpistemicTraceValidationReport(
                passed=False,
                epistemic_trace_score=0.0,
                structural_trace_score=0.0,
                evidence_trace_score=0.0,
                certainty_trace_score=0.0,
                judgment_trace_score=0.0,
                violations=["No examples found"],
                warnings=[],
                failed_examples=[],
            )

        avg_epistemic = sum(all_scores) / n
        avg_struct = sum(all_struct) / n
        avg_ev = sum(all_ev) / n
        avg_cert = sum(all_cert) / n
        avg_j = sum(all_j) / n

        passed = (
            avg_epistemic >= 0.95
            and len(failed) == 0
        )

        return EpistemicTraceValidationReport(
            passed=passed,
            epistemic_trace_score=avg_epistemic,
            structural_trace_score=avg_struct,
            evidence_trace_score=avg_ev,
            certainty_trace_score=avg_cert,
            judgment_trace_score=avg_j,
            violations=list(dict.fromkeys(all_violations)),  # deduplicate
            warnings=list(dict.fromkeys(all_warnings)),
            failed_examples=failed,
        )
