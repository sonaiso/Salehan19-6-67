"""Tests for qualification_bridge."""
from mcd.curriculum.curriculum_dataset import CurriculumDataset
from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics, compute_qualification_metrics

def _metrics():
    units = CurriculumDataset().load_all()
    return compute_qualification_metrics(units)

def test_returns_metrics_instance():
    assert isinstance(_metrics(), CurriculumQualificationMetrics)

def test_total_examples_gt_zero():
    assert _metrics().total_examples > 0

def test_golden_examples_counted():
    assert _metrics().golden_examples >= 50

def test_adversarial_examples_counted():
    assert _metrics().adversarial_examples >= 200

def test_coverage_score_between_0_and_1():
    m = _metrics()
    assert 0.0 <= m.curriculum_coverage_score <= 1.0

def test_dataset_score_above_4():
    assert _metrics().dataset_score_estimate >= 4.0

def test_recommendation_set():
    assert _metrics().recommendation

def test_to_dict_has_keys():
    d = _metrics().to_dict()
    for k in ("total_examples", "golden_examples", "adversarial_examples", "recommendation"):
        assert k in d
