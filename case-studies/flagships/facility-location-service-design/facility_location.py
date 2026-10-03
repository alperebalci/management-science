from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


FACILITIES = ("North", "Central", "South", "Coastal")
MARKETS = ("A", "B", "C", "D", "E", "F")
FIXED_COST = np.array([520.0, 610.0, 480.0, 560.0])
CAPACITY = np.array([150.0, 180.0, 140.0, 160.0])
DEMAND = np.array([55.0, 45.0, 60.0, 50.0, 40.0, 35.0])
SERVICE_COST = np.array([
    [4.0, 6.0, 9.0, 11.0, 8.0, 10.0],
    [6.0, 4.0, 5.0, 7.0, 6.0, 8.0],
    [10.0, 8.0, 5.0, 4.0, 6.0, 7.0],
    [8.0, 7.0, 7.0, 6.0, 4.0, 3.0],
])


@dataclass(frozen=True)
class FacilityLocationResult:
    open_facilities: tuple[str, ...]
    total_cost: float
    fixed_cost: float
    service_cost: float
    shipments: np.ndarray
    utilization: dict[str, float]


def solve_facility_location(max_open: int = 3) -> FacilityLocationResult:
    """Solve a capacitated facility-location MILP."""
    n_fac = len(FACILITIES)
    n_mkt = len(MARKETS)
    n_flow = n_fac * n_mkt
    n_vars = n_flow + n_fac

    c = np.concatenate([SERVICE_COST.ravel(), FIXED_COST])
    integrality = np.concatenate([np.zeros(n_flow), np.ones(n_fac)])
    lb = np.zeros(n_vars)
    ub = np.concatenate([np.full(n_flow, np.inf), np.ones(n_fac)])

    rows = []
    lower = []
    upper = []

    for j in range(n_mkt):
        row = np.zeros(n_vars)
        for i in range(n_fac):
            row[i * n_mkt + j] = 1.0
        rows.append(row)
        lower.append(DEMAND[j])
        upper.append(DEMAND[j])

    for i in range(n_fac):
        row = np.zeros(n_vars)
        row[i * n_mkt : (i + 1) * n_mkt] = 1.0
        row[n_flow + i] = -CAPACITY[i]
        rows.append(row)
        lower.append(-np.inf)
        upper.append(0.0)

    row = np.zeros(n_vars)
    row[n_flow:] = 1.0
    rows.append(row)
    lower.append(-np.inf)
    upper.append(float(max_open))

    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(np.vstack(rows), np.array(lower), np.array(upper)),
    )
    if not result.success:
        raise RuntimeError(result.message)

    flows = result.x[:n_flow].reshape(n_fac, n_mkt)
    opened = result.x[n_flow:] > 0.5
    fixed = float(FIXED_COST[opened].sum())
    service = float((flows * SERVICE_COST).sum())
    utilization = {
        FACILITIES[i]: float(flows[i].sum() / CAPACITY[i])
        for i in range(n_fac)
        if opened[i]
    }

    return FacilityLocationResult(
        open_facilities=tuple(str(x) for x in np.array(FACILITIES)[opened]),
        total_cost=float(result.fun),
        fixed_cost=fixed,
        service_cost=service,
        shipments=flows,
        utilization=utilization,
    )


def main() -> None:
    result = solve_facility_location()
    print("Recommended network")
    print("-------------------")
    print("Open facilities:", ", ".join(result.open_facilities))
    print(f"Total cost: {result.total_cost:,.2f}")
    print(f"  Fixed cost: {result.fixed_cost:,.2f}")
    print(f"  Service cost: {result.service_cost:,.2f}")

    print("\nFacility utilization")
    print("--------------------")
    for facility, utilization in result.utilization.items():
        print(f"{facility:8s}: {utilization:6.1%}")

    print("\nMarket allocation")
    print("-----------------")
    for j, market in enumerate(MARKETS):
        allocations = [
            f"{FACILITIES[i]}={result.shipments[i, j]:.0f}"
            for i in range(len(FACILITIES))
            if result.shipments[i, j] > 1e-7
        ]
        print(f"Market {market}: " + ", ".join(allocations))


if __name__ == "__main__":
    main()
