"""Deployment profile contract."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentProfile:
    name: str
    auth_required: bool
    authorization_required: bool
    rate_limit_required: bool


PROFILES: dict[str, DeploymentProfile] = {
    "local": DeploymentProfile("local", auth_required=False, authorization_required=False, rate_limit_required=False),
    "staging": DeploymentProfile("staging", auth_required=True, authorization_required=False, rate_limit_required=True),
    "production": DeploymentProfile("production", auth_required=True, authorization_required=True, rate_limit_required=True),
}


def current_profile() -> DeploymentProfile:
    key = os.environ.get("MCD_API_PROFILE", "local").strip().lower()
    return PROFILES.get(key, PROFILES["local"])

