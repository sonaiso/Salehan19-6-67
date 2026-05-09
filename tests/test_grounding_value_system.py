"""Tests for ValueSystemModel."""
import pytest
from mcd.grounding.value_system import ValueSystemModel, ValueType, JudgmentType


@pytest.fixture
def model():
    return ValueSystemModel()


def test_kadhib_dhar_practical_harmful(model):
    frames = model.analyze("الكذب ضار")
    assert len(frames) >= 1
    practical_frames = [f for f in frames if f.value_type == ValueType.PRACTICAL]
    assert len(practical_frames) >= 1
    assert practical_frames[0].judgment_type == JudgmentType.HARMFUL


def test_kadhib_haram_shari(model):
    frames = model.analyze("الكذب حرام")
    shari_frames = [f for f in frames if f.value_type == ValueType.SHARI]
    assert len(shari_frames) >= 1
    assert shari_frames[0].judgment_type == JudgmentType.HARAM


def test_shari_needs_revelation_warning(model):
    frames = model.analyze("الكذب حرام")
    shari_frames = [f for f in frames if f.value_type == ValueType.SHARI]
    assert len(shari_frames) >= 1
    assert "shari_needs_revelation_evidence" in shari_frames[0].warnings


def test_dar_not_haram_different_frames(model):
    """ضار (harmful) ≠ حرام (haram) — must be separate frames with different value_types."""
    frames = model.analyze("الكذب ضار أم حرام؟")
    practical = [f for f in frames if f.value_type == ValueType.PRACTICAL]
    shari = [f for f in frames if f.value_type == ValueType.SHARI]
    assert len(practical) >= 1
    assert len(shari) >= 1
    # They must have different value types
    assert practical[0].value_type != shari[0].value_type


def test_nafi_not_wajib(model):
    """نافع (beneficial) ≠ واجب (wajib) — must not be confused."""
    frames_nafi = model.analyze("هذا نافع")
    frames_wajib = model.analyze("هذا واجب")
    nafi_types = {f.value_type for f in frames_nafi}
    wajib_types = {f.value_type for f in frames_wajib}
    # نافع should be practical, واجب should be shari
    assert ValueType.PRACTICAL in nafi_types
    assert ValueType.SHARI in wajib_types
    # Must not overlap in judgment
    nafi_judgments = {f.judgment_type for f in frames_nafi}
    assert JudgmentType.WAJIB not in nafi_judgments


def test_shari_certainty_lower_without_revelation(model):
    frames = model.analyze("الكذب حرام")
    shari_frames = [f for f in frames if f.value_type == ValueType.SHARI]
    assert shari_frames[0].certainty < 0.6


def test_practical_certainty_not_affected_by_shari_rule(model):
    frames = model.analyze("الكذب ضار")
    practical_frames = [f for f in frames if f.value_type == ValueType.PRACTICAL]
    assert practical_frames[0].certainty >= 0.5
