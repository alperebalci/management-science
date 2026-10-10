"""Executable invariants for native Management Science flagship decision models."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1] / "case-studies" / "flagships"


def load_module(name: str, case: str, filename: str):
    """Load hyphenated case folders without modifying the source projects."""
    path = ROOT / case / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_decision_analysis_evpi_and_regret_identity():
    m = load_module("flagship_decision_analysis", "decision-analysis-capacity-expansion",
                    "decision_analysis.py")
    result = m.analyze_decision()
    assert np.allclose(result.expected_values, m.PAYOFFS @ m.PROBABILITIES)
    perfect_information = m.PAYOFFS.max(axis=0) @ m.PROBABILITIES
    assert result.evpi == pytest.approx(perfect_information - result.expected_values.max())
    assert result.evpi >= 0
    assert np.allclose(
        result.expected_regrets,
        (m.PAYOFFS.max(axis=0) - m.PAYOFFS) @ m.PROBABILITIES,
    )
    assert np.all(np.isfinite(result.certainty_equivalents))


def test_decision_analysis_rejects_bad_probabilities():
    m = load_module("flagship_decision_invalid", "decision-analysis-capacity-expansion",
                    "decision_analysis.py")
    with pytest.raises(ValueError, match="sum to one"):
        m.analyze_decision(probabilities=np.array([0.1, 0.2, 0.3]))
    with pytest.raises(ValueError, match="risk_tolerance"):
        m.analyze_decision(risk_tolerance=0)
    assert len(m.high_demand_sensitivity(np.array([0.1, 0.4]))) == 2


def test_revenue_management_booking_limits_obey_capacity():
    m = load_module("flagship_revenue_policy", "revenue-management-booking-limits",
                    "revenue_management.py")
    policy = m.emsrb_policy(capacity=120)
    assert len(policy.booking_limits) == len(m.FARE_CLASSES)
    assert np.all(policy.booking_limits >= 0)
    assert np.all(policy.booking_limits <= 120)
    assert np.allclose(policy.protection_levels + policy.booking_limits, 120)
    with pytest.raises(ValueError, match="capacity"):
        m.emsrb_policy(capacity=0)


def test_revenue_simulation_is_seed_reproducible():
    m = load_module("flagship_revenue_simulation", "revenue-management-booking-limits",
                    "revenue_management.py")
    a = m.simulate(n_replications=80, seed=23)
    b = m.simulate(n_replications=80, seed=23)
    assert a == b
    assert np.all(np.isfinite(list(a.values())))
    assert a["mean_spoilage"] >= 0
    with pytest.raises(ValueError, match="n_replications"):
        m.simulate(n_replications=0)
