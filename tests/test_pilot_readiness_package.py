from __future__ import annotations

from pathlib import Path


def test_pilot_readiness_package_contains_required_sections() -> None:
    text = Path("docs/PILOT_READINESS_PACKAGE.md").read_text(encoding="utf-8")
    for section in [
        "## Deployment Profile",
        "## Security Assumptions",
        "## Audit Report",
        "## Benchmark Report",
        "## Known Limitations",
        "## Release Notes",
    ]:
        assert section in text


def test_official_positioning_is_pilot_qualified_not_production_certified() -> None:
    text = Path("docs/PILOT_READINESS_PACKAGE.md").read_text(encoding="utf-8")
    assert "Pilot scientific-industrial qualification package" in text
    assert "not production-certified" in text
    assert "machine-checkable core proof fragments" in text
