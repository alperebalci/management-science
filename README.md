# Management Science

A curated collection of decision models, optimization formulations, and analytical case studies for management science.

The repository focuses on a practical modeling chain:

**managerial problem → decision variables → objective → constraints → uncertainty → solution → sensitivity analysis → managerial interpretation**

Rather than duplicating the full research portfolio, this repository collects a small set of representative implementations that are especially relevant to management science and links to deeper specialist repositories where appropriate.

## Core case studies

| Area | Case study | Method | Source portfolio |
|---|---|---|---|
| Inventory | Seasonal inventory planning | Mathematical programming / inventory control | [inventory-optimization-and-control](https://github.com/alperebalci/inventory-optimization-and-control) |
| Scheduling | Resource-constrained project scheduling | MILP with PuLP | [classical-scheduling-optimization](https://github.com/alperebalci/classical-scheduling-optimization) |
| Production | Multi-product demand allocation | MILP | [production-planning-optimization](https://github.com/alperebalci/production-planning-optimization) |
| Pricing | Apparel markdown optimization | Linear programming | [pricing-and-revenue-optimization](https://github.com/alperebalci/pricing-and-revenue-optimization) |
| Resource allocation | Data envelopment analysis | DEA / linear programming | [resource-allocation-optimization](https://github.com/alperebalci/resource-allocation-optimization) |
| Service systems | Jackson queueing network capacity | Queueing + optimization | [simulation-optimization-and-uncertainty-quantification](https://github.com/alperebalci/simulation-optimization-and-uncertainty-quantification) |
| Decisions under uncertainty | Stochastic project selection | Stochastic optimization / PuLP | [stochastic-programming-methods](https://github.com/alperebalci/stochastic-programming-methods) |
| Workforce | Call-center workforce optimization | Staffing / capacity planning | [workforce-optimization-and-analytics](https://github.com/alperebalci/workforce-optimization-and-analytics) |

The implementations live under `case-studies/`. Each case keeps its own dependencies and includes provenance back to the original specialist repository.

## Original flagship cases

Five cases were created specifically for this repository to cover Management Science topics that are broader than the migrated specialist examples:

| Flagship | Decision focus | Method |
|---|---|---|
| [Product Mix and Capacity Planning](case-studies/flagships/product-mix-capacity-planning/) | Production mix and bottleneck economics | LP, marginal values, sensitivity |
| [Capital Budgeting Under Risk](case-studies/flagships/capital-budgeting-under-risk/) | Investment portfolio selection | Binary MILP |
| [Facility Location and Service Design](case-studies/flagships/facility-location-service-design/) | Network footprint and market allocation | Facility-location MILP |
| [Revenue Management Booking Limits](case-studies/flagships/revenue-management-booking-limits/) | Capacity protection by fare class | EMSR-b and Monte Carlo |
| [Decision Analysis for Capacity Expansion](case-studies/flagships/decision-analysis-capacity-expansion/) | Strategic choice under uncertainty | EV, utility, EVPI, sensitivity |

See [case-studies/flagships/README.md](case-studies/flagships/README.md) for the flagship index.

## Repository structure

```text
management-science/
├── README.md
├── PORTFOLIO_MAP.md
└── case-studies/
    ├── inventory/
    │   └── seasonal-inventory-planning/
    ├── scheduling/
    │   └── resource-constrained-project-scheduling/
    ├── production/
    │   └── multi-product-demand-allocation/
    ├── pricing/
    │   └── apparel-markdown-optimization/
    ├── resource-allocation/
    │   └── data-envelopment-analysis/
    ├── service-systems/
    │   └── jackson-queueing-capacity/
    ├── uncertainty/
    │   └── stochastic-project-selection/
    └── workforce/
        └── call-center-workforce-optimization/
```

## How to use the repository

Each case study is self-contained. A typical workflow is:

```bash
cd case-studies/<area>/<case>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Some cases use `pyproject.toml` instead of `requirements.txt`; follow the local README in that directory.

## Modeling standard

When adding or reviewing a case, the preferred structure is:

1. **Decision context** — what managerial decision is being made?
2. **Inputs and assumptions** — what data and assumptions drive the model?
3. **Decision variables** — what can management control?
4. **Objective** — cost, profit, service level, utilization, risk, or a multi-objective trade-off.
5. **Constraints** — resources, demand, capacity, timing, policy, or risk limits.
6. **Uncertainty treatment** — deterministic, scenario-based, stochastic, robust, or simulation-based.
7. **Solution method** — LP, MILP, nonlinear optimization, simulation, queueing, heuristics, or related methods.
8. **Sensitivity and scenarios** — how the recommendation changes when assumptions move.
9. **Managerial interpretation** — what the solution means operationally.

## Extended portfolio

Management science overlaps with operations research, analytics, economics, and machine learning. Deeper implementations remain in specialist repositories rather than being duplicated here. See [PORTFOLIO_MAP.md](PORTFOLIO_MAP.md) for the broader map, including supply-chain design, routing, location, robust optimization, decomposition, and learning-augmented optimization.

## Scope

This repository is intentionally application-oriented. It is not intended to replace the specialist repositories or serve as a complete optimization-method taxonomy. Its purpose is to present a coherent set of management-science problems and implementations in one place.
## Licensing

The curated cases retain their source-project license terms. This repository does not impose a single replacement license across all migrated code. See [LICENSING.md](LICENSING.md) and the license file inside each case-study directory before reuse.

