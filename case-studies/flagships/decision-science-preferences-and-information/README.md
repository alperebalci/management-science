# Decision science: preferences, information and deep-uncertainty screening

**Original Management Science flagship.** This is a compact, reproducible and fully testable **normative decision-support** layer. It is not a replacement for the existing [capacity-expansion decision analysis](../decision-analysis-capacity-expansion/), which already has expected-value, regret, CARA utility, EVPI and risk/probability sensitivity. This addition introduces **imperfect information (EVSI), structured multi-criteria elicitation and rankings, and explicit probability-free robustness profiles**.

## Run

From this directory:

`python decision_science.py`

From the repository root (after installing the repository flagship-test dependencies):

`python -m pytest -q tests/test_decision_science.py`

There are no external solver or numerical dependencies in the implementation; tests use pytest.

## Models and interpretations

### 1. Bayesian decision analysis and information value

`DecisionProblem` explicitly records named states, available actions, state probabilities and monetary payoff per action/state. It provides an expected-payoff baseline, a risk-neutral perfect-information ceiling (**EVPI**) and **EVSI** for a finite discrete signal with `P(signal | state)`. Bayes' rule produces an action contingent on each observable signal. Impossible signals are excluded rather than assigned fabricated posteriors.

For a two-state/two-action 100/0 payoff example with 50/50 state probabilities and a 75%-accurate binary observation, optimal no-information value is 50, EVSI is 25, and EVPI is 50. The net value subtracts acquisition cost. The signal must be observed **before** choosing the action; these numbers do not license selecting signals after outcomes are observed.

`cara_certainty_equivalent` supports an explicit constant absolute risk-aversion utility model. Its risk tolerance is specified in the same monetary units as the payoffs; EVSI above remains **risk-neutral**, rather than using CARA for informational decisions.

### 2. Multi-criteria decision making

- **AHP**: reciprocal pairwise judgments → principal-eigenvector criterion weights and Saaty consistency ratio (CR). Inconsistent judgments are rejected by default (threshold 0.10).
- **Group AHP**: weighted geometric aggregation of individual **judgment matrices**, which preserves reciprocal structure. This is not a Delphi protocol or evidence that the experts are calibrated.
- **MAVT**: additive weighted scores using *already elicited/normalized* single-attribute value functions in [0,1]. Preferential independence and the interpretation of swing weights need to be assessed by a decision analyst. This is **not** a general multiattribute expected-utility model under risk.
- **TOPSIS**: explicit benefit/cost criteria, vector normalization, ideal/anti-ideal distances. Rankings depend on included alternatives, scales and weights; this is not a Pareto proof or an objective measure of stakeholder welfare.

AHP elicits criterion weights; MAVT evaluates a common normalized value scale; TOPSIS performs a distance-to-ideal ranking. These methods should not be interchanged without stating assumptions. Existing NSGA-II/Pareto optimizers produce candidate trade-offs rather than choosing stakeholder preferences.

### 3. Probability-free robustness screening

`deep_uncertainty_profiles` reports the number of named scenarios meeting an aspiration threshold, worst observed payoff, and maximum regret relative to the best action in each scenario. **Scenario coverage is not a probability, confidence interval or a full Robust Decision Making (RDM) workflow.** It is an auditable first step when reliable scenario probabilities are unavailable, and can motivate full stress testing and adaptive pathways.

## Validation and limitations

Deterministic tests cover EVPI ≥ EVSI ≥ 0 on oracle problems, posterior normalization, unreachable signals, consistent/inconsistent AHP, reciprocal group aggregation, monotone TOPSIS dominance, normalized MAVT, robustness/regret arithmetic, CARA numerical stability and invalid inputs.

The models are **small teaching/reference examples**, not deployed decision systems. No genuine field preference study, experimental elicitation panel, causal identification, full AHP/ANP/TOPSIS method family, ELECTRE/PROMETHEE/BWM, influence diagram, SFA, real-options valuation or social choice theory is claimed. They remain potential separate *research extensions*, not fake completed projects.
