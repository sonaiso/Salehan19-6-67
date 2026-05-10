"""Tests for Phase 8.3 CLI commands."""
import json
import sys
import pytest
from unittest.mock import patch


def run_cli(args):
    """Run CLI with given args and capture stdout."""
    import io
    from mcd.cli import main
    buf = io.StringIO()
    with patch("sys.argv", ["mcd"] + args), patch("sys.stdout", buf):
        try:
            main()
        except SystemExit:
            pass
    return buf.getvalue()


def test_jamid_analyze_insan():
    out = run_cli(["jamid-analyze", "--word", "إنسان", "--output", "json"])
    data = json.loads(out)
    assert data["found"] is True
    assert data["can_create_evidence"] is False
    assert data["can_issue_certificate"] is False


def test_mushtaq_analyze_katib():
    out = run_cli(["mushtaq-analyze", "--word", "كاتب", "--output", "json"])
    data = json.loads(out)
    assert data["derivation_type"] == "ism_faail"
    assert data["can_create_evidence"] is False
    assert data["can_prove_event_occurred"] is False


def test_concept_geometry_graph_maktab():
    out = run_cli(["concept-geometry-graph", "--word", "مكتب", "--output", "json"])
    data = json.loads(out)
    assert "nodes" in data
    assert data["word"] == "مكتب"


def test_concept_geometry_validate():
    out = run_cli(["concept-geometry-validate", "--output", "json"])
    data = json.loads(out)
    assert data["passed"] is True
    assert data["concept_geometry_score"] >= 0.95
