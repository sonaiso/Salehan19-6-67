"""Tests for KPI Schema."""
from mcd.evaluation.kpi_schema import KPI, build_kpi_registry, KPICategory, KPIStatus


def test_kpi_registry_has_20_kpis():
    kpis = build_kpi_registry()
    assert len(kpis) >= 20, f"Expected ≥20 KPIs, got {len(kpis)}"


def test_kpi_registry_has_required_ids():
    kpis = build_kpi_registry()
    ids = {k.kpi_id for k in kpis}
    required = {"EQ-01", "EQ-02", "EQ-03", "EQ-04", "EQ-05", "EQ-06",
                "PC-01", "PC-02", "PC-03", "PC-04",
                "RQ-01", "RQ-02", "RQ-03", "RQ-04",
                "IN-01", "IN-02", "IN-03", "IN-04", "IN-05", "IN-06"}
    missing = required - ids
    assert not missing, f"Missing KPI IDs: {missing}"


def test_kpi_categories_cover_all():
    kpis = build_kpi_registry()
    categories = {k.category for k in kpis}
    expected = {c.value for c in KPICategory}
    assert expected == categories, f"Missing categories: {expected - categories}"


def test_kpi_status_values_valid():
    kpis = build_kpi_registry()
    valid = {s.value for s in KPIStatus}
    for kpi in kpis:
        assert kpi.status in valid, f"Invalid status: {kpi.status}"


def test_kpi_to_dict():
    kpis = build_kpi_registry()
    for kpi in kpis:
        d = kpi.to_dict()
        assert "kpi_id" in d
        assert "name" in d
        assert "formula" in d
        assert "target_value" in d


def test_kpi_target_values_reasonable():
    kpis = build_kpi_registry()
    for kpi in kpis:
        assert kpi.target_value >= 0.0, f"Negative target: {kpi.kpi_id}"
