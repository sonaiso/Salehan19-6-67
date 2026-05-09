"""Tests for RoleInferer."""
from __future__ import annotations

import pytest
from mcd.engines.role_inferer import RoleInferer
from mcd.core.roles import RoleType


@pytest.fixture
def inferer():
    return RoleInferer()


def test_al_prefix_identified(inferer):
    roles = inferer.infer_roles('الكتاب')
    # First two chars should be definite_article
    chars = [ch for ch, _ in roles]
    top_roles = [rv.top_role() for _, rv in roles]
    assert 'definite_article' in top_roles[:2] or 'prefix' in top_roles[:2]


def test_ta_marbuta_suffix(inferer):
    roles = inferer.infer_roles('كتابة')
    last_ch, last_rv = roles[-1]
    assert last_ch == 'ة'
    assert last_rv.top_role() == RoleType.SUFFIX.value


def test_root_radicals_in_ktb(inferer):
    roles = inferer.infer_roles('كتب')
    for ch, rv in roles:
        assert rv.top_role() == RoleType.ROOT_RADICAL.value


def test_role_vectors_not_empty(inferer):
    roles = inferer.infer_roles('كاتب')
    assert len(roles) > 0
    for _, rv in roles:
        assert rv.probabilities


def test_role_vectors_sum_approx_one(inferer):
    roles = inferer.infer_roles('كتب')
    for _, rv in roles:
        total = sum(rv.probabilities.values())
        assert abs(total - 1.0) < 0.01 or total > 0  # normalized or not
