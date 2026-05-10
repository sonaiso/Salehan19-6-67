"""Tests for TraceValidator."""
import pytest
from mcd.traceability.trace_builder import TraceBuilder, TraceBundle
from mcd.traceability.trace_validator import TraceValidator, TraceValidationReport


@pytest.fixture
def builder():
    return TraceBuilder()


@pytest.fixture
def validator():
    return TraceValidator()


def test_valid_bundle_passes(builder, validator):
    bundle = builder.build("كتب زيد الدرس")
    report = validator.validate(bundle)
    assert report.passed is True
    assert report.traceability_score >= 0.99


def test_all_unicode_traced(builder, validator):
    text = "كتب زيد الدرس بالقلم في المدرسة أمس"
    bundle = builder.build(text)
    report = validator.validate(bundle)
    assert report.total_unicode == len(text)
    assert report.traced_unicode == len(text)


def test_no_orphan_tokens(builder, validator):
    bundle = builder.build("مرحبا بالعالم")
    report = validator.validate(bundle)
    assert report.orphan_tokens == 0


def test_empty_bundle(validator):
    builder = TraceBuilder()
    bundle = builder.build("")
    report = validator.validate(bundle)
    # Empty but still needs judgment
    assert report.total_unicode == 0


def test_report_to_dict(builder, validator):
    bundle = builder.build("كتب")
    report = validator.validate(bundle)
    d = report.to_dict()
    assert "passed" in d
    assert "traceability_score" in d
    assert "violations" in d


def test_report_to_markdown(builder, validator):
    bundle = builder.build("كتب")
    report = validator.validate(bundle)
    md = report.to_markdown()
    assert "Trace Validation Report" in md
    assert "traceability_score" in md


def test_missing_evidence_bundle(builder, validator):
    bundle = builder.build("هذا صحيح بلا مصدر")
    report = validator.validate(bundle)
    # Should still pass (traceability is structural, not about content)
    assert report.total_unicode == len("هذا صحيح بلا مصدر")
    assert report.traced_unicode == report.total_unicode


def test_no_orphan_vectors(builder, validator):
    bundle = builder.build("كتب زيد")
    report = validator.validate(bundle)
    assert report.orphan_vectors == 0
