from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from revenue_management import simulate


def main() -> None:
    capacities = np.arange(80, 181, 10)
    emsr = []
    fcfs = []
    lift = []

    print("Capacity sensitivity")
    for capacity in capacities:
        result = simulate(capacity=int(capacity))
        emsr.append(result["emsr_mean_revenue"])
        fcfs.append(result["fcfs_mean_revenue"])
        lift.append(result["revenue_lift"])
        print(
            f"{capacity:4d} seats -> EMSR-b={result['emsr_mean_revenue']:9.2f} | "
            f"FCFS={result['fcfs_mean_revenue']:9.2f} | "
            f"lift={result['revenue_lift']:8.2f}"
        )

    figures = Path(__file__).resolve().parent / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.plot(capacities, emsr, marker="o", label="EMSR-b")
    plt.plot(capacities, fcfs, marker="o", label="FCFS")
    plt.xlabel("Capacity")
    plt.ylabel("Mean revenue")
    plt.title("Revenue Management: Value of Booking Control")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "capacity-revenue-sensitivity.svg")
    plt.close()


if __name__ == "__main__":
    main()
