from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import linprog


PRODUCTS = ("Standard", "Premium", "Industrial", "Eco")
CONTRIBUTION_MARGIN = np.array([48.0, 72.0, 58.0, 40.0])
MACHINE_HOURS = np.array([2.0, 4.0, 3.0, 1.5])
LABOR_HOURS = np.array([4.0, 5.0, 3.0, 2.0])
MATERIAL_UNITS = np.array([3.0, 5.0, 4.0, 2.5])
DEMAND_CAPS = np.array([120.0, 80.0, 90.0, 140.0])


@dataclass(frozen=True)
class ProductMixResult:
    quantities: np.ndarray
    contribution: float
    resource_slack: dict[str, float]
    shadow_values: dict[str, float]


def solve_product_mix(
    machine_capacity: float = 420.0,
    labor_capacity: float = 500.0,
    material_capacity: float = 650.0,
    margins: np.ndarray | None = None,
) -> ProductMixResult:
    """Solve a contribution-maximizing product-mix LP."""
    unit_margin = CONTRIBUTION_MARGIN if margins is None else np.asarray(margins, dtype=float)
    if unit_margin.shape != (len(PRODUCTS),):
        raise ValueError("margins must contain one value per product")

    a_ub = np.vstack([MACHINE_HOURS, LABOR_HOURS, MATERIAL_UNITS, np.eye(len(PRODUCTS))])
    b_ub = np.concatenate([
        np.array([machine_capacity, labor_capacity, material_capacity], dtype=float),
        DEMAND_CAPS,
    ])

    result = linprog(
        c=-unit_margin,
        A_ub=a_ub,
        b_ub=b_ub,
        bounds=[(0, None)] * len(PRODUCTS),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    resource_names = ("machine", "labor", "material")
    resource_slack = {
        name: float(result.ineqlin.residual[i]) for i, name in enumerate(resource_names)
    }
    shadow_values = {
        name: float(-result.ineqlin.marginals[i]) for i, name in enumerate(resource_names)
    }

    return ProductMixResult(
        quantities=result.x,
        contribution=float(-result.fun),
        resource_slack=resource_slack,
        shadow_values=shadow_values,
    )


def capacity_sensitivity(resource: str, levels: Iterable[float]) -> list[tuple[float, float]]:
    """Re-solve the model over alternative capacity levels."""
    if resource not in {"machine", "labor", "material"}:
        raise ValueError("resource must be machine, labor, or material")

    rows = []
    for level in levels:
        kwargs = {
            "machine_capacity": 420.0,
            "labor_capacity": 500.0,
            "material_capacity": 650.0,
        }
        kwargs[f"{resource}_capacity"] = float(level)
        solution = solve_product_mix(**kwargs)
        rows.append((float(level), solution.contribution))
    return rows


def main() -> None:
    solution = solve_product_mix()
    print("Optimal product mix")
    print("-------------------")
    for product, quantity in zip(PRODUCTS, solution.quantities):
        print(f"{product:12s}: {quantity:8.2f}")
    print(f"\nTotal contribution: {solution.contribution:,.2f}")

    print("\nResource diagnostics")
    print("--------------------")
    for name in ("machine", "labor", "material"):
        print(
            f"{name:8s}: slack={solution.resource_slack[name]:8.2f}, "
            f"marginal value={solution.shadow_values[name]:8.2f}"
        )

    print("\nMachine-capacity sensitivity")
    print("----------------------------")
    for capacity, contribution in capacity_sensitivity("machine", [360, 390, 420, 450, 480]):
        print(f"{capacity:8.0f} hours -> {contribution:10.2f}")


if __name__ == "__main__":
    main()
