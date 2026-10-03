from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


PROJECTS = ("Automation", "New Market", "Analytics Platform", "Green Retrofit", "Service Expansion", "R&D Pilot")
NPV = np.array([180.0, 240.0, 150.0, 130.0, 210.0, 170.0])
CAPEX = np.array([110.0, 160.0, 90.0, 75.0, 140.0, 100.0])
MANAGEMENT_CAPACITY = np.array([4.0, 6.0, 3.0, 2.0, 5.0, 4.0])
RISK_SCORE = np.array([2.0, 5.0, 2.0, 1.0, 4.0, 5.0])


@dataclass(frozen=True)
class CapitalBudgetResult:
    selected: tuple[str, ...]
    total_npv: float
    capital_used: float
    management_used: float
    risk_used: float


def solve_capital_budget(
    capital_budget: float = 350.0,
    management_limit: float = 12.0,
    risk_limit: float = 9.0,
) -> CapitalBudgetResult:
    """Select projects using a binary capital-budgeting MILP."""
    n = len(PROJECTS)

    rows = [CAPEX, MANAGEMENT_CAPACITY, RISK_SCORE]
    lower = [-np.inf, -np.inf, -np.inf]
    upper = [capital_budget, management_limit, risk_limit]

    dependency = np.zeros(n)
    dependency[1] = 1.0
    dependency[2] = -1.0
    rows.append(dependency)
    lower.append(-np.inf)
    upper.append(0.0)

    exclusivity = np.zeros(n)
    exclusivity[0] = 1.0
    exclusivity[3] = 1.0
    rows.append(exclusivity)
    lower.append(-np.inf)
    upper.append(1.0)

    result = milp(
        c=-NPV,
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=LinearConstraint(np.vstack(rows), np.array(lower), np.array(upper)),
    )
    if not result.success:
        raise RuntimeError(result.message)

    chosen = result.x > 0.5
    return CapitalBudgetResult(
        selected=tuple(str(x) for x in np.array(PROJECTS)[chosen]),
        total_npv=float(NPV[chosen].sum()),
        capital_used=float(CAPEX[chosen].sum()),
        management_used=float(MANAGEMENT_CAPACITY[chosen].sum()),
        risk_used=float(RISK_SCORE[chosen].sum()),
    )


def budget_frontier(budgets: list[float]) -> list[tuple[float, float, tuple[str, ...]]]:
    """Return the efficient project portfolio across alternative capital budgets."""
    rows = []
    for budget in budgets:
        result = solve_capital_budget(capital_budget=budget)
        rows.append((budget, result.total_npv, result.selected))
    return rows


def main() -> None:
    result = solve_capital_budget()
    print("Recommended capital portfolio")
    print("-----------------------------")
    for project in result.selected:
        print(f"- {project}")
    print(f"\nTotal NPV: {result.total_npv:,.0f}")
    print(f"Capital used: {result.capital_used:,.0f} / 350")
    print(f"Management capacity used: {result.management_used:,.0f} / 12")
    print(f"Risk score used: {result.risk_used:,.0f} / 9")

    print("\nBudget frontier")
    print("---------------")
    for budget, value, projects in budget_frontier([250, 300, 350, 400, 450]):
        print(f"{budget:5.0f} -> NPV {value:6.0f} | {', '.join(projects)}")


if __name__ == "__main__":
    main()
