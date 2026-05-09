"""End-to-end tests for GroundedReasoningBuilder."""
import pytest
from mcd.grounding.grounded_reasoning_builder import GroundedReasoningBuilder
from mcd.grounding.grounded_frame import GroundedReasoningFrame
from mcd.grounding.value_system import ValueType


@pytest.fixture
def builder():
    return GroundedReasoningBuilder()


def test_kataba_has_role_frames(builder):
    frame = builder.build("كتب زيد الدرس بالقلم في المدرسة أمس")
    assert isinstance(frame, GroundedReasoningFrame)
    assert len(frame.role_frames) >= 1


def test_kataba_has_nisbah_frames(builder):
    frame = builder.build("كتب زيد الدرس بالقلم في المدرسة أمس")
    assert len(frame.nisbah_frames) >= 3


def test_kataba_has_grounded_lexemes(builder):
    frame = builder.build("كتب زيد الدرس بالقلم في المدرسة أمس")
    assert len(frame.grounded_lexemes) >= 1


def test_value_frames_distinguish_practical_shari(builder):
    """الكذب ضار أم حرام؟ → must have both practical and shari value frames."""
    frame = builder.build("الكذب ضار أم حرام؟")
    assert len(frame.value_frames) >= 2
    value_types = {vf.value_type for vf in frame.value_frames}
    assert ValueType.PRACTICAL in value_types
    assert ValueType.SHARI in value_types


def test_civilization_frames_for_ai(builder):
    frame = builder.build("الذكاء الاصطناعي أداة مدنية أم مفهوم حضاري؟")
    assert len(frame.civilization_frames) >= 1


def test_social_frames_with_uncertainty(builder):
    frame = builder.build("المجتمع يرفض الفساد")
    assert len(frame.social_frames) >= 1
    social = frame.social_frames[0]
    certainty = social.get("certainty", 0.0) if isinstance(social, dict) else getattr(social, "certainty", 0.0)
    assert certainty < 0.5


def test_final_status_set(builder):
    frame = builder.build("كتب زيد الدرس بالقلم في المدرسة أمس")
    assert frame.final_status in ("grounded", "partially_grounded", "ungrounded")


def test_certainty_summary_non_negative(builder):
    frame = builder.build("النار ساخنة")
    assert frame.certainty_summary >= 0.0


def test_input_text_preserved(builder):
    text = "كتب زيد الدرس"
    frame = builder.build(text)
    assert frame.input_text == text
