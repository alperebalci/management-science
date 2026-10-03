from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from product_mix import capacity_sensitivity, solve_product_mix


def main() -> None:
    levels = np.arange(330.0, 481.0, 15.0)
    rows = capacity_sensitivity("machine", levels)
    capacities = np.array([row[0] for row in rows])
    contributions = np.array([row[1] for row in rows])

    baseline = solve_product_mix()
    print("Baseline resource economics")
    for resource in ("machine", "labor", "material"):
        print(
            f"{resource:8s} slack={baseline.resource_slack[resource]:7.2f} "
            f"marginal_value={baseline.shadow_values[resource]:7.2f}"
        )

    print("\nMachine-capacity frontier")
    for capacity, contribution in rows:
        print(f"{capacity:7.0f} -> {contribution:10.2f}")

    figures = Path(__file__).resolve().parent / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.plot(capacities, contributions, marker="o")
    plt.axvline(420.0, linestyle="--", linewidth=1)
    plt.xlabel("Machine capacity (hours)")
    plt.ylabel("Optimal contribution")
    plt.title("Product Mix: Machine-Capacity Sensitivity")
    plt.tight_layout()
    plt.savefig(figures / "machine-capacity-sensitivity.svg")
    plt.close()


if __name__ == "__main__":
    main()
