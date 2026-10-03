# Original Management Science Flagships

These cases were created specifically for this repository to complement the curated projects drawn from specialist repositories.

| Flagship | Core question | Method |
|---|---|---|
| [Product Mix and Capacity Planning](product-mix-capacity-planning/) | What should we produce and which bottleneck should we expand? | LP, shadow values, sensitivity |
| [Capital Budgeting Under Risk](capital-budgeting-under-risk/) | Which investment portfolio should receive scarce capital? | Binary MILP, portfolio constraints |
| [Facility Location and Service Design](facility-location-service-design/) | Which sites should open and how should markets be served? | Capacitated facility-location MILP |
| [Revenue Management Booking Limits](revenue-management-booking-limits/) | How much capacity should be protected for high-value demand? | EMSR-b, Monte Carlo simulation |
| [Decision Analysis for Capacity Expansion](decision-analysis-capacity-expansion/) | Which strategic capacity choice is preferred under uncertainty? | EV, regret, utility, EVPI, sensitivity |

The five cases deliberately span optimization, network design, revenue management, and decision analysis rather than concentrating only on mathematical programming.

## Decision-support layer

Each flagship now includes a reproducible `analysis.py`, a pre-rendered SVG sensitivity figure, explicit baseline results, threshold/scenario analysis, and a managerial-insights section. The intent is to show not only the optimum, but also **why the recommendation changes and which assumptions management should monitor**.
