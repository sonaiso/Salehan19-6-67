"""Structured governance logging."""
from __future__ import annotations

import json
import logging


def get_governance_logger() -> logging.Logger:
    logger = logging.getLogger("mcd.governance")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_governance_event(event: dict) -> None:
    get_governance_logger().info(json.dumps(event, ensure_ascii=False))

