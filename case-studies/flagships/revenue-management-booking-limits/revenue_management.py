from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


FARE_CLASSES = ("Business", "Flex", "Saver", "Basic")
FARES = np.array([420.0, 300.0, 190.0, 110.0])
MEAN_DEMAND = np.array([18.0, 32.0, 50.0, 75.0])
STD_DEMAND = np.array([6.0, 9.0, 12.0, 18.0])
CAPACITY = 120


@dataclass(frozen=True)
class RevenuePolicy:
    protection_levels: np.ndarray
    booking_limits: np.ndarray


def emsrb_policy(capacity: int = CAPACITY) -> RevenuePolicy:
    """Compute nested EMSR-b protection levels and booking limits."""
    if capacity <= 0:
        raise ValueError("capacity must be positive")

    n = len(FARE_CLASSES)
    protection = np.zeros(n)
    booking_limits = np.full(n, float(capacity))

    for j in range(1, n):
        higher_mean = MEAN_DEMAND[:j]
        higher_std = STD_DEMAND[:j]
        aggregated_mean = float(higher_mean.sum())
        aggregated_std = float(np.sqrt(np.square(higher_std).sum()))
        weighted_fare = float(np.dot(FARES[:j], higher_mean) / aggregated_mean)

        critical_ratio = 1.0 - FARES[j] / weighted_fare
        critical_ratio = float(np.clip(critical_ratio, 1e-6, 1 - 1e-6))
        protection[j] = np.clip(
            aggregated_mean + aggregated_std * norm.ppf(critical_ratio),
            0.0,
            float(capacity),
        )
        booking_limits[j] = capacity - protection[j]

    return RevenuePolicy(protection_levels=protection, booking_limits=booking_limits)


def _sell_low_to_high(demand: np.ndarray, booking_limits: np.ndarray) -> np.ndarray:
    """Process lower fares first, subject to nested booking limits."""
    accepted = np.zeros_like(demand, dtype=float)
    total_sold = 0.0

    for j in range(len(demand) - 1, -1, -1):
        room = max(0.0, booking_limits[j] - total_sold)
        accepted[j] = min(float(demand[j]), room)
        total_sold += accepted[j]

    return accepted


def simulate(
    n_replications: int = 5000,
    seed: int = 42,
    capacity: int = CAPACITY,
) -> dict[str, float]:
    """Compare EMSR-b with unrestricted first-come-first-served sales."""
    if n_replications <= 0:
        raise ValueError("n_replications must be positive")

    rng = np.random.default_rng(seed)
    policy = emsrb_policy(capacity)

    emsr_revenue = []
    fcfs_revenue = []
    emsr_spoilage = []

    for _ in range(n_replications):
        demand = np.maximum(0, np.rint(rng.normal(MEAN_DEMAND, STD_DEMAND)))

        emsr_sales = _sell_low_to_high(demand, policy.booking_limits)
        fcfs_sales = _sell_low_to_high(
            demand,
            np.full(len(FARE_CLASSES), float(capacity)),
        )

        emsr_revenue.append(float(np.dot(emsr_sales, FARES)))
        fcfs_revenue.append(float(np.dot(fcfs_sales, FARES)))
        emsr_spoilage.append(float(capacity - emsr_sales.sum()))

    emsr = np.asarray(emsr_revenue)
    fcfs = np.asarray(fcfs_revenue)
    spoilage = np.asarray(emsr_spoilage)

    return {
        "emsr_mean_revenue": float(emsr.mean()),
        "fcfs_mean_revenue": float(fcfs.mean()),
        "revenue_lift": float(emsr.mean() - fcfs.mean()),
        "emsr_revenue_std": float(emsr.std(ddof=1)),
        "mean_spoilage": float(spoilage.mean()),
    }


def main() -> None:
    policy = emsrb_policy()

    print("EMSR-b nested booking policy")
    print("----------------------------")
    for i, fare_class in enumerate(FARE_CLASSES):
        print(
            f"{fare_class:8s} fare={FARES[i]:6.0f} | "
            f"protection={policy.protection_levels[i]:6.1f} | "
            f"booking limit={policy.booking_limits[i]:6.1f}"
        )

    results = simulate()
    print("\nSimulation comparison")
    print("---------------------")
    print(f"EMSR-b mean revenue: {results['emsr_mean_revenue']:,.2f}")
    print(f"FCFS mean revenue:   {results['fcfs_mean_revenue']:,.2f}")
    print(f"Revenue lift:        {results['revenue_lift']:,.2f}")
    print(f"Mean unsold capacity under EMSR-b: {results['mean_spoilage']:.2f}")


if __name__ == "__main__":
    main()
