"""Governance audit report builders."""
from __future__ import annotations

import json

from mcd.audit.replay import replay_trace_events, reconstruct_certificate_forensics


def build_governance_audit_report(events: list[dict]) -> dict:
    replay = replay_trace_events(events).to_dict()
    forensic = reconstruct_certificate_forensics(events)
    return {
        "replay": replay,
        "forensics": forensic,
        "governance_status": "ok" if replay["replay_success"] else "requires_attention",
    }


def governance_audit_report_json(events: list[dict]) -> str:
    return json.dumps(build_governance_audit_report(events), ensure_ascii=False, indent=2)

