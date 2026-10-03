from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from decision_analysis import ALTERNATIVES, PAYOFFS, analyze_decision


def main() -> None:
    probabilities = np.linspace(0.05, 0.60, 12)
    expected_values = []

    print("High-demand probability sensitivity")
    for p_high in probabilities:
        remaining = 1.0 - p_high
        p = np.array([remaining / 3.0, 2.0 * remaining / 3.0, p_high])
        values = PAYOFFS @ p
        expected_values.append(values)
        choice = ALTERNATIVES[int(np.argmax(values))]
        print(f"P(high)={p_high:5.0%} -> {choice:15s} | best EV={values.max():7.2f}")

    print("\nRisk-tolerance sensitivity")
    for tolerance in [60, 90, 120, 180, 240, 360, 1000]:
        result = analyze_decision(risk_tolerance=float(tolerance))
        choice = ALTERNATIVES[int(np.argmax(result.certainty_equivalents))]
        print(f"R={tolerance:4d} -> {choice:15s}")

    values = np.asarray(expected_values)
    figures = Path(__file__).resolve().parent / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    for i, alternative in enumerate(ALTERNATIVES):
        plt.plot(probabilities, values[:, i], marker="o", label=alternative)
    plt.xlabel("Probability of high demand")
    plt.ylabel("Expected NPV")
    plt.title("Decision Analysis: Probability Sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "probability-sensitivity.svg")
    plt.close()


if __name__ == "__main__":
    main()
