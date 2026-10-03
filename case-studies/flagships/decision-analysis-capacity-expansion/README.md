# Decision Analysis for Capacity Expansion

An original Management Science flagship combining risk-neutral decision analysis, regret, risk aversion, value of information, and probability sensitivity.

## Management question

Should management keep the current footprint, lease flexible capacity, or build a permanent facility when future demand is uncertain?

## Method

The case evaluates three alternatives across low, base, and high demand states using:

- expected monetary value,
- expected regret,
- exponential utility and certainty equivalents,
- expected value of perfect information (EVPI),
- one-way probability sensitivity.

## Run

~~~bash
pip install -r requirements.txt
python decision_analysis.py
~~~

## Managerial interpretation

A risk-neutral recommendation can differ from a risk-adjusted recommendation because large downside outcomes matter differently to decision makers with finite risk tolerance. EVPI sets an upper bound on what management should pay for perfect demand information, while sensitivity analysis identifies when the preferred strategy changes.

All payoffs and probabilities are synthetic and created specifically for this flagship case.
