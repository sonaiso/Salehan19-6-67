"""ConceptGeometryReport — report generation for Phase 8.3."""
from __future__ import annotations

import json
from typing import Union

from mcd.concept_geometry.jamid_schema import JamidEssence
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit


def generate_jamid_report(jamid_essence: JamidEssence, output: str = "markdown") -> str:
    """Generate a report for a JamidEssence."""
    if output == "json":
        return json.dumps(jamid_essence.to_dict(), ensure_ascii=False, indent=2)

    et = jamid_essence.essence_type.value if hasattr(jamid_essence.essence_type, "value") else str(jamid_essence.essence_type)
    lines = [
        f"# Jamid Essence: {jamid_essence.surface}",
        "",
        f"**Essence Type:** {et}",
        f"**Genus:** {jamid_essence.genus}",
        f"**Species:** {jamid_essence.species}",
        "",
        "## Differentia",
    ]
    for d in jamid_essence.differentia:
        lines.append(f"- {d}")
    lines += [
        "",
        "## Intrinsic Properties",
    ]
    for p in jamid_essence.intrinsic_properties:
        lines.append(f"- {p}")
    lines += [
        "",
        "## Essence Vector",
    ]
    for k, v in jamid_essence.essence_vector.items():
        lines.append(f"- {k}: {v:.2f}")
    lines += [
        "",
        "## CFK Contract",
        f"- can_create_evidence: {jamid_essence.can_create_evidence}",
        f"- can_issue_certificate: {jamid_essence.can_issue_certificate}",
        f"- evidence_state: {jamid_essence.evidence_state}",
        f"- certainty_policy: {jamid_essence.certainty_policy}",
    ]
    return "\n".join(lines)


def generate_mushtaq_report(mushtaq_unit: MushtaqUnit, output: str = "markdown") -> str:
    """Generate a report for a MushtaqUnit."""
    if output == "json":
        return json.dumps(mushtaq_unit.to_dict(), ensure_ascii=False, indent=2)

    dt = mushtaq_unit.derivation_type.value if hasattr(mushtaq_unit.derivation_type, "value") else str(mushtaq_unit.derivation_type)
    pr = mushtaq_unit.projected_relation.value if hasattr(mushtaq_unit.projected_relation, "value") else str(mushtaq_unit.projected_relation)
    lines = [
        f"# Mushtaq Unit: {mushtaq_unit.surface}",
        "",
        f"**Root:** {mushtaq_unit.root}",
        f"**Pattern:** {mushtaq_unit.pattern}",
        f"**Derivation Type:** {dt}",
        f"**Folded Event:** {mushtaq_unit.folded_event or '—'}",
        f"**Projected Relation:** {pr}",
        "",
        "## Role Vector",
    ]
    for k, v in mushtaq_unit.role_vector.items():
        lines.append(f"- {k}: {v:.2f}")
    if mushtaq_unit.candidate_relations:
        lines += ["", "## Candidate Relations (context required)"]
        for r in mushtaq_unit.candidate_relations:
            lines.append(f"- {r}")
    lines += [
        "",
        "## CFK Contract",
        f"- can_create_evidence: {mushtaq_unit.can_create_evidence}",
        f"- can_issue_certificate: {mushtaq_unit.can_issue_certificate}",
        f"- can_prove_event_occurred: {mushtaq_unit.can_prove_event_occurred}",
        f"- certainty_policy: {mushtaq_unit.certainty_policy}",
    ]
    return "\n".join(lines)


def generate_json_report(obj: Union[JamidEssence, MushtaqUnit]) -> str:
    """Generate JSON report for any schema object."""
    return json.dumps(obj.to_dict(), ensure_ascii=False, indent=2)
