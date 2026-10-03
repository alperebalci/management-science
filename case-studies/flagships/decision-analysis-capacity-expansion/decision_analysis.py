from __future__ import annotations

from dataclasses import dataclass

import numpy as np


ALTERNATIVES = ("Status Quo", "Lease Capacity", "Build Facility")
STATES = ("Low Demand", "Base Demand", "High Demand")
PROBABILITIES = np.array([0.25, 0.50, 0.25])

# Illustrative NPVs in thousands of currency units.
PAYOFFS = np.array([
    [90.0, 120.0, 145.0],
    [55.0, 175.0, 260.0],
    [-60.0, 205.0, 390.0],
])


@dataclass(frozen=True)
class DecisionAnalysis:
    expected_values: np.ndarray
    expected_regrets: np.ndarray
    certainty_equivalents: np.ndarray
    evpi: float


def analyze_decision(
    probabilities: np.ndarray = PROBABILITIES,
    risk_tolerance: float = 180.0,
) -> DecisionAnalysis:
    """Evaluate alternatives using EV, regret, risk-adjusted utility, and EVPI."""
    p = np.asarray(probabilities, dtype=float)
    if p.shape != (len(STATES),) or np.any(p < 0) or not np.isclose(p.sum(), 1.0):
        raise ValueError("probabilities must be nonnegative and sum to one")
    if risk_tolerance <= 0:
        raise ValueError("risk_tolerance must be positive")

    expected_values = PAYOFFS @ p

    best_by_state = PAYOFFS.max(axis=0)
    regrets = best_by_state - PAYOFFS
    expected_regrets = regrets @ p

    utilities = -np.exp(-PAYOFFS / risk_tolerance)
    expected_utility = utilities @ p
    certainty_equivalents = -risk_tolerance * np.log(-expected_utility)

    expected_value_with_perfect_information = float(best_by_state @ p)
    evpi = expected_value_with_perfect_information - float(expected_values.max())

    return DecisionAnalysis(
        expected_values=expected_values,
        expected_regrets=expected_regrets,
        certainty_equivalents=certainty_equivalents,
        evpi=evpi,
    )


def high_demand_sensitivity(grid: np.ndarray | None = None) -> list[tuple[float, str, float]]:
    """Vary high-demand probability and preserve a 1:2 low/base ratio."""
    if grid is None:
        grid = np.linspace(0.05, 0.60, 12)

    rows = []
    for p_high in np.asarray(grid, dtype=float):
        if not 0 <= p_high < 1:
            raise ValueError("high-demand probabilities must lie in [0, 1)")
        remaining = 1.0 - p_high
        probabilities = np.array([remaining / 3.0, 2.0 * remaining / 3.0, p_high])
        expected_values = PAYOFFS @ probabilities
        best = int(np.argmax(expected_values))
        rows.append((float(p_high), ALTERNATIVES[best], float(expected_values[best])))
    return rows


def main() -> None:
    result = analyze_decision()

    print("Decision analysis")
    print("-----------------")
    for i, alternative in enumerate(ALTERNATIVES):
        print(
            f"{alternative:15s} | EV={result.expected_values[i]:7.2f} | "
            f"expected regret={result.expected_regrets[i]:7.2f} | "
            f"certainty equivalent={result.certainty_equivalents[i]:7.2f}"
        )

    ev_choice = ALTERNATIVES[int(np.argmax(result.expected_values))]
    risk_choice = ALTERNATIVES[int(np.argmax(result.certainty_equivalents))]
    print(f"\nRisk-neutral choice: {ev_choice}")
    print(f"Risk-adjusted choice: {risk_choice}")
    print(f"EVPI: {result.evpi:.2f}")

    print("\nHigh-demand probability sensitivity")
    print("-----------------------------------")
    for p_high, choice, value in high_demand_sensitivity():
        print(f"P(high)={p_high:4.0%} -> {choice:15s} | EV={value:7.2f}")


if __name__ == "__main__":
    main()
