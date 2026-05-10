"""Tests for Phase 8 CFK CLI commands."""
from __future__ import annotations

import json
import sys
from io import StringIO

import pytest


def _run_cli(*args: str) -> tuple[str, int]:
    """Run the CLI with given args and return (stdout, exit_code)."""
    from mcd.cli import main
    old_argv = sys.argv
    old_stdout = sys.stdout
    captured = StringIO()
    sys.stdout = captured
    sys.argv = ["mcd"] + list(args)
    exit_code = 0
    try:
        main()
    except SystemExit as e:
        exit_code = int(e.code) if e.code is not None else 0
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
    return captured.getvalue(), exit_code


class TestCFKAnalyzeCLI:
    def test_cfk_analyze_text_output(self):
        out, code = _run_cli("cfk-analyze", "--text", "إن هذا لحق", "--output", "text")
        assert code == 0
        assert "الحكم" in out

    def test_cfk_analyze_json_output(self):
        out, code = _run_cli("cfk-analyze", "--text", "إن هذا لحق", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert "proof" in d
        assert d["proof"]["judgment"] in ("certificate", "hypothesis", "suspend", "zero")

    def test_cfk_analyze_markdown_output(self):
        out, code = _run_cli("cfk-analyze", "--text", "زيد كاتب", "--output", "markdown")
        assert code == 0
        assert "تقرير النواة" in out

    def test_cfk_analyze_with_evidence(self):
        out, code = _run_cli(
            "cfk-analyze", "--text", "النار حارة",
            "--evidence", "empirical_1,experimental_2",
            "--output", "text",
        )
        assert code == 0
        assert "الحكم" in out


class TestCFKCompareCLI:
    def test_cfk_compare_text_output(self):
        out, code = _run_cli("cfk-compare", "--text", "كل الشركات تستخدم هذه التقنية", "--output", "text")
        assert code == 0
        assert "البعد" in out or "GPT" in out or "الحكم" in out

    def test_cfk_compare_json_output(self):
        out, code = _run_cli("cfk-compare", "--text", "زيد كاتب", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert "rows" in d
        assert len(d["rows"]) == 5

    def test_cfk_compare_markdown_output(self):
        out, code = _run_cli("cfk-compare", "--text", "إن زيداً لكريم", "--output", "markdown")
        assert code == 0
        assert "|" in out  # markdown table

    def test_cfk_compare_kernel_judgment_in_json(self):
        out, code = _run_cli("cfk-compare", "--text", "زيد كاتب", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert d["kernel_judgment"] in ("certificate", "hypothesis", "suspend", "zero")


class TestCFKProofCLI:
    def test_cfk_proof_text_output(self):
        out, code = _run_cli("cfk-proof", "--text", "إن هذا لحق", "--output", "text")
        assert code == 0
        assert "الحكم" in out

    def test_cfk_proof_json_output(self):
        out, code = _run_cli("cfk-proof", "--text", "كل الشركات تستخدم شيئاً", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert "judgment" in d
        assert d["judgment"] in ("certificate", "hypothesis", "suspend", "zero")

    def test_cfk_proof_shows_residual(self):
        out, code = _run_cli("cfk-proof", "--text", "إن هذا لحق", "--output", "text")
        assert code == 0
        assert "الباقي" in out

    def test_cfk_proof_evidence_state_in_output(self):
        out, code = _run_cli("cfk-proof", "--text", "زيد كاتب", "--output", "text")
        assert code == 0
        assert "الدليل" in out or "evidence" in out.lower()

    def test_cfk_proof_universal_is_suspend(self):
        out, code = _run_cli("cfk-proof", "--text", "كل الشركات تستخدم GraphRAG", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert d["judgment"] == "suspend"

    def test_cfk_proof_with_evidence(self):
        out, code = _run_cli(
            "cfk-proof", "--text", "النار حارة",
            "--evidence", "e1,e2",
            "--output", "text",
        )
        assert code == 0
        assert "الحكم" in out


class TestCFKTableCLI:
    def test_cfk_table_markdown(self):
        out, code = _run_cli("cfk-table", "--text", "إن هذا لحق", "--output", "markdown")
        assert code == 0
        assert "جدول المقارنة" in out
        assert "|" in out

    def test_cfk_table_json(self):
        out, code = _run_cli("cfk-table", "--text", "زيد كاتب", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert "rows" in d
        assert "kernel_judgment" in d

    def test_cfk_table_has_five_rows(self):
        out, code = _run_cli("cfk-table", "--text", "زيد كاتب", "--output", "json")
        assert code == 0
        d = json.loads(out)
        assert len(d["rows"]) == 5

    def test_cfk_table_row_has_three_columns(self):
        out, code = _run_cli("cfk-table", "--text", "test", "--output", "json")
        assert code == 0
        d = json.loads(out)
        for row in d["rows"]:
            assert "statistical" in row
            assert "arabic" in row
            assert "epistemic" in row
