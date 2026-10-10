"""Independent numerical oracles and adverse inputs for normative decision science."""

import importlib.util
import math
import sys
from pathlib import Path

import pytest

PATH = (Path(__file__).resolve().parents[1] / "case-studies" / "flagships" /
        "decision-science-preferences-and-information" / "decision_science.py")
SPEC = importlib.util.spec_from_file_location("native_decision_science_lab", PATH)
assert SPEC is not None and SPEC.loader is not None
ds = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ds
SPEC.loader.exec_module(ds)


def binary_problem():
    return ds.DecisionProblem(("A", "B"), ("good", "bad"), (0.5, 0.5),
                              ((100, 0), (0, 100)))


def test_information_oracle_and_posterior_coherence():
    problem = binary_problem()
    result = ds.value_of_sample_information(problem, ((0.75, 0.25), (0.25, 0.75)))
    assert ds.expected_payoffs(problem) == (50, 50)
    assert ds.best_expected_action(problem) == ("A", 50)
    assert ds.evpi(problem) == pytest.approx(50)
    assert result.evsi == pytest.approx(25)
    assert result.evpi == pytest.approx(50)
    assert result.net_value == pytest.approx(25)
    assert result.signal_probabilities == pytest.approx((0.5, 0.5))
    assert result.posteriors[0] == pytest.approx((0.75, 0.25))
    assert result.posteriors[1] == pytest.approx((0.25, 0.75))
    assert result.conditional_actions == ("A", "B")
    assert sum(result.signal_probabilities) == pytest.approx(1)


def test_no_information_and_perfect_information_limits():
    p = binary_problem()
    no_info = ds.value_of_sample_information(p, ((0.5, 0.5), (0.5, 0.5)), 2)
    perfect = ds.value_of_sample_information(p, ((1, 0), (0, 1)), 2)
    assert no_info.evsi == pytest.approx(0)
    assert no_info.net_value == pytest.approx(-2)
    assert perfect.evsi == pytest.approx(perfect.evpi)
    assert perfect.net_value == pytest.approx(48)
    impossible = ds.value_of_sample_information(p, ((1, 0), (1, 0)))
    assert impossible.conditional_actions[1] is None
    assert impossible.posteriors[1] is None


def test_cara_certainty_equivalent_and_numerical_stability():
    assert ds.cara_certainty_equivalent((10, 10), (0.4, 0.6), 0.001) == pytest.approx(10)
    ce = ds.cara_certainty_equivalent((0, 100), (0.5, 0.5), 25)
    assert 0 < ce < 50
    huge = ds.cara_certainty_equivalent((100000, 100010), (0.5, 0.5), 10)
    assert 100000 < huge < 100010


def test_deep_uncertainty_scores_are_not_probabilities():
    profiles = ds.deep_uncertainty_profiles(
        ("Flexible", "Aggressive"), ("A", "B", "C"),
        ((80, 90, 100), (120, 10, 200)), aspiration=75,
    )
    assert profiles[0].meeting_scenarios == 3
    assert profiles[0].scenario_coverage == pytest.approx(1)
    assert profiles[1].meeting_scenarios == 2
    assert profiles[1].worst_payoff == 10
    assert profiles[1].maximum_regret == 80


def test_ahp_consistent_ratios_and_group_aggregation():
    a = ((1, 2, 6), (0.5, 1, 3), (1 / 6, 1 / 3, 1))
    result = ds.ahp_priorities(a)
    assert result.weights == pytest.approx((0.6, 0.3, 0.1), rel=1e-8)
    assert result.consistency_ratio == pytest.approx(0, abs=1e-9)
    merged = ds.aggregate_ahp_judgments((a, a), (0.4, 0.6))
    for i in range(3):
        for j in range(3):
            assert merged[i][j] == pytest.approx(a[i][j])


def test_ahp_rejects_inconsistency_and_nonreciprocity():
    a = ((1, 9, 1 / 9), (1 / 9, 1, 9), (9, 1 / 9, 1))
    with pytest.raises(ValueError, match="inconsistent"):
        ds.ahp_priorities(a)
    result = ds.ahp_priorities(a, reject_inconsistent=False)
    assert not result.is_consistent
    assert result.consistency_ratio > 0.1
    with pytest.raises(ValueError, match="reciprocal"):
        ds.ahp_priorities(((1, 2), (2, 1)))
    with pytest.raises(ValueError, match="expert weight"):
        ds.aggregate_ahp_judgments((a, a), (1.0,))


def test_mavt_is_normalized_and_topsis_respects_dominance():
    assert ds.additive_value(((0.8, 0.4), (0.5, 0.9)), (0.7, 0.3)) == pytest.approx((0.68, 0.62))
    scores = ds.topsis_scores(((10, 1), (5, 4)), (0.5, 0.5), ("benefit", "cost"))
    assert scores == pytest.approx((1.0, 0.0))
    assert ds.topsis_scores(((0, 0), (0, 0)), (0.5, 0.5), ("cost", "benefit")) == (0.5, 0.5)
    with pytest.raises(ValueError, match="already lie"):
        ds.additive_value(((10, 20),), (0.5, 0.5))


def test_invalid_inputs_cannot_silently_make_recommendations():
    with pytest.raises(ValueError, match="sum to one"):
        ds.DecisionProblem(("A",), ("S1", "S2"), (0.2, 0.2), ((1, 2),))
    with pytest.raises(ValueError, match="incompatible"):
        ds.DecisionProblem(("A",), ("S1", "S2"), (0.5, 0.5), ((1,),))
    with pytest.raises(ValueError, match="finite"):
        ds.DecisionProblem(("A",), ("S",), (1,), ((math.nan,),))
    with pytest.raises(ValueError, match="sum to one"):
        ds.value_of_sample_information(binary_problem(), ((0.6, 0.6), (0.5, 0.5)))
    with pytest.raises(ValueError, match="nonnegative"):
        ds.value_of_sample_information(binary_problem(), ((1, 0), (0, 1)), -1)
    with pytest.raises(ValueError, match="direction"):
        ds.topsis_scores(((1, 2),), (0.5, 0.5), ("benefit", "unknown"))
    with pytest.raises(ValueError, match="risk_tolerance"):
        ds.cara_certainty_equivalent((1, 2), (0.5, 0.5), 0)
