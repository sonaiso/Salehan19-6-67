from mcd.coding_copilot.coding_status import (
    CodingStatus,
    PUBLIC_FINAL_CODING_JUDGMENTS,
    collapse_to_public_status,
    is_public_final_coding_judgment,
)


def test_only_three_public_coding_judgments():
    assert set(PUBLIC_FINAL_CODING_JUDGMENTS) == {
        CodingStatus.ZERO.value,
        CodingStatus.HYPOTHESIS.value,
        CodingStatus.CERTIFICATE.value,
    }


def test_pass_fail_are_not_final_judgments():
    assert is_public_final_coding_judgment("pass") is False
    assert is_public_final_coding_judgment("fail") is False


def test_suspend_collapses_to_hypothesis():
    assert collapse_to_public_status("suspend") == CodingStatus.HYPOTHESIS.value
