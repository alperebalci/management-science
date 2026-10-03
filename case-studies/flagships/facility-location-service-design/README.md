# Facility Location and Service Network Design

An original Management Science flagship on deciding which facilities to open and how markets should be assigned when fixed costs, service costs, and capacity interact.

## Management question

Which candidate facilities should be opened, and how should demand be allocated across the network?

## Model

The capacitated facility-location MILP minimizes:

- facility fixed-opening cost,
- demand-weighted service/transport cost.

Subject to:

- every market being fully served,
- facility capacity,
- service only from open facilities,
- a strategic limit on the number of active facilities.

## Run

~~~bash
pip install -r requirements.txt
python facility_location.py
~~~

## Managerial interpretation

The model exposes the classic fixed-cost versus responsiveness trade-off. A larger network can reduce customer-serving cost but increases structural cost and complexity. Capacity utilization also indicates whether the chosen footprint contains resilience or is operating near saturation.

All data are synthetic and created specifically for this flagship case.
