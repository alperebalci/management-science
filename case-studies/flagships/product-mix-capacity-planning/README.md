# Product Mix and Capacity Planning

An original Management Science case study on choosing a profit-maximizing product portfolio under scarce machine, labor, material, and demand capacity.

## Management question

Which products should management produce, in what quantities, and which constrained resource is worth expanding?

## Model

The linear program maximizes total contribution margin subject to:

- machine-hour capacity,
- labor-hour capacity,
- material availability,
- product-specific demand ceilings,
- nonnegative production quantities.

The implementation also reports resource slack and marginal resource values from the LP solution, then re-solves the model across alternative capacity levels.

## Run

~~~bash
pip install -r requirements.txt
python product_mix.py
~~~

## Managerial interpretation

The optimal mix is only part of the decision. Binding constraints and marginal values indicate where an additional unit of capacity has economic value. Capacity sensitivity shows when that value disappears because another resource or market demand becomes the next bottleneck.

All data are synthetic and created specifically for this flagship case.
