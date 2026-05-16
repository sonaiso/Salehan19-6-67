from __future__ import annotations

from dataclasses import dataclass, field

from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit

ASCENT_LEVELS: list[str] = [
    "raw_text",
    "unicode",
    "grapheme",
    "orthographic_unit",
    "token",
    "lexeme",
    "morphology",
    "phrase",
    "clause",
    "sentence",
    "paragraph",
    "section",
    "full_text",
    "discourse_graph",
    "claim_graph",
    "proof_object",
    "final_judgment",
]

FINAL_JUDGMENTS = {"zero", "hypothesis", "certificate"}
VALID_BETA_STATUSES = {"undefined", "invalid", "valid_uncertified", "valid_certified"}
VALID_TRANSITION_BETA = {"valid_uncertified", "valid_certified"}
CONSTITUTIONAL_FORBIDDEN_TRANSITIONS = {
    "root_or_pattern_as_factual_proof",
    "derivative_as_proof",
    "irab_as_factual_certainty",
    "emphasis_as_evidence",
    "metaphor_as_literal_certificate",
    "memory_as_external_evidence",
    "model_output_as_evidence",
    "tool_output_as_certificate_without_governance",
    "residual_erasure",
    "silent_level_skip",
    "certificate_without_proof_object",
    "certificate_without_governance_gate",
    "certificate_without_reverse_trace",
}


@dataclass
class TextAscentValidationReport:
    passed: bool
    violations: list[str] = field(default_factory=list)


def _can_reach_level(start: GovernedFractalUnit, unit_map: dict[str, GovernedFractalUnit], target_level: str) -> bool:
    seen: set[str] = set()
    stack: list[str] = [start.unit_id]
    while stack:
        uid = stack.pop()
        if uid in seen:
            continue
        seen.add(uid)
        unit = unit_map.get(uid)
        if unit is None:
            continue
        if unit.level_id == target_level:
            return True
        stack.extend(unit.pre_unit_ids)
    return False


def validate_text_ascent_chain(units: list[GovernedFractalUnit]) -> TextAscentValidationReport:
    violations: list[str] = []
    if not units:
        return TextAscentValidationReport(passed=False, violations=["text ascent chain is empty"])

    by_id = {u.unit_id: u for u in units}
    level_order = {name: i for i, name in enumerate(ASCENT_LEVELS)}
    first_seen: dict[str, int] = {}
    for i, u in enumerate(units):
        if u.level_id not in first_seen:
            first_seen[u.level_id] = i

    # Enforce explicit Unicode-to-FullText/ClaimGraph coverage.
    missing_levels = [lvl for lvl in ASCENT_LEVELS if lvl not in first_seen]
    for lvl in missing_levels:
        violations.append(f"missing ascent level: {lvl}")

    if not missing_levels:
        for i in range(len(ASCENT_LEVELS) - 1):
            src_level = ASCENT_LEVELS[i]
            tgt_level = ASCENT_LEVELS[i + 1]
            if first_seen[src_level] >= first_seen[tgt_level]:
                violations.append(f"ascent order invalid: {src_level} must appear before {tgt_level}")
                continue
            src = units[first_seen[src_level]]
            tgt = units[first_seen[tgt_level]]
            if tgt.unit_id not in src.post_unit_ids:
                violations.append(f"{src.unit_id}: missing post link to {tgt.unit_id} ({src_level}->{tgt_level})")
            if not src.pre_to_post_relation:
                violations.append(f"{src.unit_id}: pre_to_post_relation is required for {src_level}->{tgt_level}")
            if src.beta_status not in VALID_TRANSITION_BETA:
                violations.append(
                    f"{src.unit_id}: beta_status '{src.beta_status}' is invalid for transition {src_level}->{tgt_level}"
                )

    for unit in units:
        declared_forbidden = unit.metadata.get("forbidden_transitions", [])
        normalized = {(item or "").strip().lower() for item in declared_forbidden}
        blocked = sorted(normalized.intersection(CONSTITUTIONAL_FORBIDDEN_TRANSITIONS))
        if blocked:
            violations.append(f"{unit.unit_id}: forbidden transitions detected: {blocked}")

        for post_id in unit.post_unit_ids:
            target = by_id.get(post_id)
            if target is None:
                continue
            src_idx = level_order.get(unit.level_id)
            tgt_idx = level_order.get(target.level_id)
            if src_idx is None or tgt_idx is None:
                continue
            if tgt_idx - src_idx != 1:
                violations.append(
                    f"{unit.unit_id}: silent_level_skip {unit.level_id}->{target.level_id} is forbidden"
                )

    final_units = [u for u in units if u.level_id == "final_judgment"]
    if not final_units:
        violations.append("missing final_judgment unit")
    else:
        for unit in final_units:
            if unit.unit_type not in FINAL_JUDGMENTS:
                violations.append(
                    f"{unit.unit_id}: final judgment must be one of {sorted(FINAL_JUDGMENTS)}"
                )
            if not unit.trace_refs:
                violations.append(f"{unit.unit_id}: final judgment requires trace_refs")
            if not _can_reach_level(unit, by_id, "raw_text"):
                violations.append(f"{unit.unit_id}: reverse trace does not reach raw_text")
            if not _can_reach_level(unit, by_id, "unicode"):
                violations.append(f"{unit.unit_id}: reverse trace does not reach unicode")
            if not _can_reach_level(unit, by_id, "full_text"):
                violations.append(f"{unit.unit_id}: reverse trace does not reach full_text")
            if not _can_reach_level(unit, by_id, "claim_graph"):
                violations.append(f"{unit.unit_id}: reverse trace does not reach claim_graph")
            if unit.unit_type == "certificate" and unit.beta_status != "valid_certified":
                violations.append(f"{unit.unit_id}: certificate requires beta_status=valid_certified")
            if unit.unit_type == "certificate" and unit.residuals:
                violations.append(f"{unit.unit_id}: certificate cannot erase or bypass residuals")
            if unit.unit_type == "certificate" and not _can_reach_level(unit, by_id, "proof_object"):
                violations.append(
                    f"{unit.unit_id}: certificate_without_proof_object is forbidden"
                )
            governance_passed = bool(
                unit.metadata.get("governance_gate_passed", unit.beta_status == "valid_certified")
            )
            if unit.unit_type == "certificate" and not governance_passed:
                violations.append(
                    f"{unit.unit_id}: certificate_without_governance_gate is forbidden"
                )
            reverse_trace_complete = bool(unit.metadata.get("reverse_trace_complete", bool(unit.trace_refs)))
            if unit.unit_type == "certificate" and not reverse_trace_complete:
                violations.append(
                    f"{unit.unit_id}: certificate_without_reverse_trace is forbidden"
                )

    return TextAscentValidationReport(passed=len(violations) == 0, violations=violations)
