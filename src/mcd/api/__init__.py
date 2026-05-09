"""Phase 6 — Minimal REST API package for Minimal Cognitive Decoder."""
from __future__ import annotations

__all__ = ["create_app"]


def create_app():
    """Factory function — import deferred so FastAPI is optional at import time."""
    from mcd.api.app import build_app
    return build_app()
