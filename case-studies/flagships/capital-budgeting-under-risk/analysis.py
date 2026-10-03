from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from capital_budgeting import solve_capital_budget


def main() -> None:
    budgets = np.arange(200.0, 501.0, 25.0)
    budget_values = np.array([solve_capital_budget(capital_budget=b).total_npv for b in budgets])

    risk_limits = np.arange(4.0, 13.0, 1.0)
    risk_values = np.array([solve_capital_budget(risk_limit=r).total_npv for r in risk_limits])

    print("Budget sensitivity")
    for budget, value in zip(budgets, budget_values):
        result = solve_capital_budget(capital_budget=float(budget))
        print(f"{budget:6.0f} -> NPV={value:6.0f} | {', '.join(result.selected)}")

    print("\nRisk-limit sensitivity")
    for limit, value in zip(risk_limits, risk_values):
        result = solve_capital_budget(risk_limit=float(limit))
        print(f"{limit:6.0f} -> NPV={value:6.0f} | {', '.join(result.selected)}")

    figures = Path(__file__).resolve().parent / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.step(budgets, budget_values, where="post", marker="o")
    plt.xlabel("Capital budget")
    plt.ylabel("Optimal portfolio NPV")
    plt.title("Capital Budgeting: Value of Additional Funding")
    plt.tight_layout()
    plt.savefig(figures / "budget-frontier.svg")
    plt.close()


if __name__ == "__main__":
    main()
