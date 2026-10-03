# Capital Budgeting Under Strategic Constraints

An original Management Science case study on selecting a portfolio of investment projects when capital, management attention, implementation dependencies, and risk tolerance are limited.

## Management question

Which projects should the firm fund this cycle, and how does the optimal portfolio change as the capital budget changes?

## Model

A binary mixed-integer model maximizes portfolio NPV subject to:

- total capital expenditure,
- limited management capacity,
- portfolio risk exposure,
- project dependency,
- mutually exclusive implementation windows.

A budget-frontier analysis re-solves the model over several funding levels.

## Run

~~~bash
pip install -r requirements.txt
python capital_budgeting.py
~~~

## Managerial interpretation

The case emphasizes that capital budgeting is not simply ranking projects by NPV. Interdependencies, scarce managerial bandwidth, and portfolio risk can make a lower-ranked project part of the optimal portfolio while a high-NPV project is rejected.

All data are synthetic and created specifically for this flagship case.
