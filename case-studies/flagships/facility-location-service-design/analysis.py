from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from facility_location import solve_facility_location


def main() -> None:
    demand_scales = np.arange(0.75, 1.21, 0.05)
    total_costs = []
    print("Demand sensitivity")
    for scale in demand_scales:
        result = solve_facility_location(demand_scale=float(scale))
        total_costs.append(result.total_cost)
        print(
            f"{scale:5.0%} demand -> cost={result.total_cost:8.2f} | "
            f"open={', '.join(result.open_facilities)}"
        )

    fixed_scales = [0.75, 1.0, 1.25, 1.5]
    print("\nFixed-cost sensitivity")
    for scale in fixed_scales:
        result = solve_facility_location(fixed_cost_scale=scale)
        print(
            f"{scale:5.0%} fixed cost -> cost={result.total_cost:8.2f} | "
            f"open={', '.join(result.open_facilities)}"
        )

    figures = Path(__file__).resolve().parent / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.plot(demand_scales, total_costs, marker="o")
    plt.axvline(1.0, linestyle="--", linewidth=1)
    plt.xlabel("Demand scale")
    plt.ylabel("Optimal network cost")
    plt.title("Facility Location: Demand Sensitivity")
    plt.tight_layout()
    plt.savefig(figures / "demand-sensitivity.svg")
    plt.close()


if __name__ == "__main__":
    main()
