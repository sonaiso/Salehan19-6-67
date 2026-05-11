from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence


def test_evidence_ids_are_stable():
    te = TestEvidence("pytest -q", True)
    se = StaticEvidence("ruff", True)
    ae = ArchitectureEvidence([], [], True)
    assert te.evidence_id.startswith("test::")
    assert se.evidence_id == "static::ruff"
    assert ae.evidence_id == "architecture::governance"
