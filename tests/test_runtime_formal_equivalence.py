from __future__ import annotations

import json
from pathlib import Path

from mcd.qualification.runtime_formal_equivalence import runtime_formal_truth_table


def test_runtime_formal_truth_table_matches_committed_artifact() -> None:
    runtime_table = runtime_formal_truth_table()
    committed = json.loads(Path("research/formal/runtime_formal_equivalence_truth_table.json").read_text(encoding="utf-8"))

    runtime_by_case = {row["case_id"]: row for row in runtime_table}
    committed_by_case = {row["case_id"]: row for row in committed["truth_table"]}

    assert set(runtime_by_case) == set(committed_by_case)
    for case_id, runtime_row in runtime_by_case.items():
        committed_row = committed_by_case[case_id]
        assert runtime_row["python_public_judgment"] == committed_row["python_public_judgment"]
        assert runtime_row["lean_public_judgment"] == committed_row["lean_public_judgment"]
        assert runtime_row["equivalent"] == "true"


def test_runtime_formal_truth_table_covers_certificate_rank_and_residual_gates() -> None:
    rows = {row["case_id"]: row for row in runtime_formal_truth_table()}
    assert rows["T01-certificate-allowed"]["python_public_judgment"] == "certificate"
    assert rows["T08-insufficient-rank"]["python_public_judgment"] == "hypothesis"
    assert rows["T07-residual-erasure"]["python_public_judgment"] == "hypothesis"
