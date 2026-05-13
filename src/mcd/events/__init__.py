"""Governance event sourcing primitives."""
from __future__ import annotations

from mcd.events.log import GovernanceEventRecord, ImmutableGovernanceEventLog

__all__ = ["GovernanceEventRecord", "ImmutableGovernanceEventLog"]
