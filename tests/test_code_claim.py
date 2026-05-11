from mcd.coding_copilot.code_claim import CodeClaim


def test_code_claim_required_evidence_check():
    claim = CodeClaim(
        claim_id="C-1",
        claim_type="fixes_bug",
        affected_files=["src/a.py"],
        expected_effect="fix bug",
        required_evidence=["test::pytest tests/test_a.py -q"],
    )
    assert claim.has_required_evidence({"test::pytest tests/test_a.py -q"}) is True
    assert claim.has_required_evidence(set()) is False
