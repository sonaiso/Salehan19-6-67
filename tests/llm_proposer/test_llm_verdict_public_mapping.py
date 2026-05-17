from __future__ import annotations

import pytest

from mcd.llm_proposer.verdict_mapping import public_judgment_to_verdict, verdict_to_public_judgment


def test_zero_maps_to_zero() -> None:
    assert verdict_to_public_judgment("ZERO") == "zero"


def test_hypothesis_maps_to_hypothesis() -> None:
    assert verdict_to_public_judgment("HYPOTHESIS") == "hypothesis"


def test_certificate_maps_to_certificate() -> None:
    assert verdict_to_public_judgment("CERTIFICATE") == "certificate"


def test_unknown_verdict_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unknown llm_proposer verdict"):
        verdict_to_public_judgment("MERGED")


def test_unknown_public_judgment_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unknown public judgment"):
        public_judgment_to_verdict("merged")
