# Revenue Management with EMSR-b Booking Limits

An original Management Science flagship implementing a classic nested booking-control policy for a capacity-constrained service.

## Management question

How much capacity should be protected for higher-paying customers when lower-fare demand arrives earlier and future demand is uncertain?

## Method

The case implements EMSR-b:

- fare classes are ordered from high to low,
- higher-class demand is aggregated,
- a protection level is calculated using demand uncertainty and relative fares,
- nested booking limits control how much low-fare demand is accepted.

A Monte Carlo experiment compares EMSR-b with unrestricted first-come-first-served sales.

## Run

~~~bash
pip install -r requirements.txt
python revenue_management.py
~~~

## Managerial interpretation

Accepting every low-fare request can fill capacity before high-value demand arrives. Protecting too much capacity creates spoilage. Revenue management balances these two risks rather than treating every unit of demand as economically equivalent.

All demand distributions and fares are synthetic and created specifically for this flagship case.
