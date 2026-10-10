"""Small, auditable normative decision science and multi-criteria models.

No hidden data, stochastic fitting, solver calls or external dependencies.
Inputs are synthetic unless supplied explicitly by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isclose, isfinite, log, sqrt
from typing import Sequence


def _finite(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def _probabilities(values: Sequence[float], label: str = "probabilities") -> tuple[float, ...]:
    p = tuple(_finite(x, label) for x in values)
    if not p or any(x < 0 for x in p) or not isclose(sum(p), 1.0, abs_tol=1e-9, rel_tol=0):
        raise ValueError(f"{label} must be nonnegative and sum to one")
    return p


def _rectangular(rows: Sequence[Sequence[float]], label: str) -> tuple[tuple[float, ...], ...]:
    matrix = tuple(tuple(_finite(x, label) for x in row) for row in rows)
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError(f"{label} must be a nonempty rectangular matrix")
    return matrix


def _names(names: Sequence[str], label: str) -> tuple[str, ...]:
    result = tuple(names)
    if not result or any(not isinstance(n, str) or not n.strip() for n in result):
        raise ValueError(f"{label} must contain nonempty strings")
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must have unique names")
    return result


@dataclass(frozen=True)
class DecisionProblem:
    actions: tuple[str, ...]
    states: tuple[str, ...]
    probabilities: tuple[float, ...]
    payoffs: tuple[tuple[float, ...], ...]  # action x state; higher is better

    def __post_init__(self) -> None:
        actions = _names(self.actions, "actions")
        states = _names(self.states, "states")
        p = _probabilities(self.probabilities)
        q = _rectangular(self.payoffs, "payoffs")
        if len(states) != len(p) or len(q) != len(actions) or any(len(row) != len(states) for row in q):
            raise ValueError("payoffs, actions, states and probabilities have incompatible dimensions")


def expected_payoffs(problem: DecisionProblem) -> tuple[float, ...]:
    return tuple(sum(p * x for p, x in zip(problem.probabilities, row)) for row in problem.payoffs)


def best_expected_action(problem: DecisionProblem) -> tuple[str, float]:
    values = expected_payoffs(problem)
    k = max(range(len(values)), key=values.__getitem__)
    return problem.actions[k], values[k]


def evpi(problem: DecisionProblem) -> float:
    """Risk-neutral expected value of perfect state information, before costs."""
    expected_perfect = sum(
        probability * max(row[s] for row in problem.payoffs)
        for s, probability in enumerate(problem.probabilities)
    )
    return max(0.0, expected_perfect - best_expected_action(problem)[1])


@dataclass(frozen=True)
class SampleInformation:
    """Bayesian pre-posterior decision result for an imperfect discrete signal."""
    signal_probabilities: tuple[float, ...]
    posteriors: tuple[tuple[float, ...] | None, ...]
    conditional_actions: tuple[str | None, ...]
    evsi: float
    evpi: float
    acquisition_cost: float
    net_value: float


def value_of_sample_information(
    problem: DecisionProblem,
    signal_likelihoods: Sequence[Sequence[float]],
    acquisition_cost: float = 0.0,
) -> SampleInformation:
    """likelihoods[state][signal] = P(signal | state); risk-neutral EVSI.

    The signal must arrive BEFORE the action. A signal with zero marginal
    probability is unreachable and has no posterior or contingent decision.
    """
    likelihoods = _rectangular(signal_likelihoods, "signal likelihoods")
    if len(likelihoods) != len(problem.states):
        raise ValueError("signal likelihoods must have one row per state")
    for row in likelihoods:
        _probabilities(row, "signal likelihoods row")
    cost = _finite(acquisition_cost, "acquisition cost")
    if cost < 0:
        raise ValueError("acquisition cost must be nonnegative")

    marginal: list[float] = []
    posteriors: list[tuple[float, ...] | None] = []
    recommendations: list[str | None] = []
    with_signal = 0.0
    for j in range(len(likelihoods[0])):
        joint = [problem.probabilities[s] * likelihoods[s][j] for s in range(len(problem.states))]
        mass = sum(joint)
        marginal.append(mass)
        if mass == 0:
            posteriors.append(None)
            recommendations.append(None)
            continue
        posterior = tuple(weight / mass for weight in joint)
        posteriors.append(posterior)
        action_values = [sum(w * payoff for w, payoff in zip(joint, row)) for row in problem.payoffs]
        k = max(range(len(action_values)), key=action_values.__getitem__)
        with_signal += action_values[k]
        recommendations.append(problem.actions[k])

    value = with_signal - best_expected_action(problem)[1]
    # Only eliminate sub-floating-point noise; never hide material negative EVSI.
    if abs(value) < 1e-10:
        value = 0.0
    ceiling = evpi(problem)
    if value < -1e-8 or value > ceiling + 1e-8:
        raise AssertionError("information inequality violated; check signal model")
    return SampleInformation(tuple(marginal), tuple(posteriors), tuple(recommendations),
                             value, ceiling, cost, value - cost)


def cara_certainty_equivalent(outcomes: Sequence[float], probabilities: Sequence[float],
                              risk_tolerance: float) -> float:
    """Numerically stable exponential/CARA certainty equivalent of monetary payoffs."""
    p = _probabilities(probabilities)
    x = tuple(_finite(v, "outcomes") for v in outcomes)
    r = _finite(risk_tolerance, "risk_tolerance")
    if len(x) != len(p):
        raise ValueError("outcomes and probabilities must have equal length")
    if r <= 0:
        raise ValueError("risk_tolerance must be positive")
    terms = [-v / r for v, weight in zip(x, p) if weight > 0]
    maximum = max(terms)
    weighted = sum(weight * exp(-v / r - maximum) for v, weight in zip(x, p) if weight > 0)
    return -r * (maximum + log(weighted))


@dataclass(frozen=True)
class RobustnessScore:
    action: str
    meeting_scenarios: int
    total_scenarios: int
    worst_payoff: float
    maximum_regret: float

    @property
    def scenario_coverage(self) -> float:
        """Fraction of NAMED scenarios passing the threshold; not a probability."""
        return self.meeting_scenarios / self.total_scenarios


def deep_uncertainty_profiles(actions: Sequence[str], states: Sequence[str],
                              payoffs: Sequence[Sequence[float]], aspiration: float) -> tuple[RobustnessScore, ...]:
    """Unweighted, probability-free scenario-stress screening (NOT a calibrated RDM)."""
    labels = _names(actions, "actions")
    state_labels = _names(states, "states")
    matrix = _rectangular(payoffs, "payoffs")
    target = _finite(aspiration, "aspiration")
    if len(matrix) != len(labels) or any(len(row) != len(state_labels) for row in matrix):
        raise ValueError("scenario payoffs have incompatible dimensions")
    best_per_state = [max(row[j] for row in matrix) for j in range(len(state_labels))]
    return tuple(
        RobustnessScore(labels[i], sum(v >= target for v in row), len(state_labels),
                        min(row), max(best_per_state[j] - value for j, value in enumerate(row)))
        for i, row in enumerate(matrix)
    )


@dataclass(frozen=True)
class AHPResult:
    weights: tuple[float, ...]
    consistency_ratio: float
    is_consistent: bool


_RI = (0.0, 0.0, 0.0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49)


def _pairwise(judgments: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
    a = _rectangular(judgments, "pairwise judgments")
    n = len(a)
    if n > 10 or any(len(row) != n for row in a):
        raise ValueError("AHP requires square pairwise matrices with 1-10 criteria")
    for i in range(n):
        for j in range(n):
            if a[i][j] <= 0 or not isclose(a[i][j] * a[j][i], 1.0, rel_tol=1e-7, abs_tol=1e-9):
                raise ValueError("AHP judgments must be positive and reciprocal")
    return a


def ahp_priorities(judgments: Sequence[Sequence[float]], *,
                   reject_inconsistent: bool = True, consistency_threshold: float = 0.10) -> AHPResult:
    """Principal eigenvector priority; Saaty CR for n<=10, with n<=2 defined CR=0."""
    a = _pairwise(judgments)
    threshold = _finite(consistency_threshold, "consistency_threshold")
    if threshold < 0:
        raise ValueError("consistency_threshold must be nonnegative")
    n = len(a)
    w = [1 / n] * n
    for _ in range(10000):
        updated = [sum(a[i][j] * w[j] for j in range(n)) for i in range(n)]
        total = sum(updated)
        updated = [x / total for x in updated]
        if max(abs(updated[i] - w[i]) for i in range(n)) < 1e-13:
            w = updated
            break
        w = updated
    else:
        raise ArithmeticError("AHP priority iteration did not converge")

    if n <= 2:
        cr = 0.0
    else:
        eigenvalue = sum(sum(a[i][j] * w[j] for j in range(n)) / w[i] for i in range(n)) / n
        cr = max(0.0, (eigenvalue - n) / ((n - 1) * _RI[n]))
    consistent = cr <= threshold + 1e-12
    if reject_inconsistent and not consistent:
        raise ValueError(f"AHP pairwise judgments are inconsistent: CR={cr:.3f}")
    return AHPResult(tuple(w), cr, consistent)


def aggregate_ahp_judgments(matrices: Sequence[Sequence[Sequence[float]]],
                            expert_weights: Sequence[float]) -> tuple[tuple[float, ...], ...]:
    """Group AHP via weighted geometric aggregation of *judgments* (AIJ)."""
    opinions = tuple(_pairwise(x) for x in matrices)
    weights = _probabilities(expert_weights, "expert weights")
    if len(opinions) != len(weights):
        raise ValueError("one expert weight per pairwise matrix is required")
    n = len(opinions[0])
    if any(len(a) != n for a in opinions):
        raise ValueError("all experts must judge the same number of criteria")
    return tuple(tuple(exp(sum(weight * log(a[i][j]) for weight, a in zip(weights, opinions)))
                       for j in range(n)) for i in range(n))


def _weights(values: Sequence[float], n: int) -> tuple[float, ...]:
    weights = _probabilities(values, "criteria weights")
    if len(weights) != n:
        raise ValueError("criteria weights have incompatible dimension")
    return weights


def additive_value(utilities: Sequence[Sequence[float]], weights: Sequence[float]) -> tuple[float, ...]:
    """MAVT: weighted additive scores of *elicited 0..1 single-attribute values*.

    It is not a substitute for preferential independence or multiattribute
    expected utility under risk. Do not feed unscaled raw criteria here.
    """
    u = _rectangular(utilities, "single-attribute values")
    w = _weights(weights, len(u[0]))
    if any(v < 0 or v > 1 for row in u for v in row):
        raise ValueError("single-attribute values must already lie in [0, 1]")
    return tuple(sum(v * weight for v, weight in zip(row, w)) for row in u)


def topsis_scores(values: Sequence[Sequence[float]], weights: Sequence[float],
                  directions: Sequence[str]) -> tuple[float, ...]:
    """Vector-normalized TOPSIS; direction is 'benefit' or 'cost' per criterion."""
    x = _rectangular(values, "decision matrix")
    n_criteria = len(x[0])
    w = _weights(weights, n_criteria)
    if len(directions) != n_criteria or any(d not in ("benefit", "cost") for d in directions):
        raise ValueError("one benefit/cost direction per criterion is required")
    norm = [sqrt(sum(row[j] ** 2 for row in x)) for j in range(n_criteria)]
    normalized = [
        [w[j] * (row[j] / norm[j] if norm[j] > 0 else 0.0) for j in range(n_criteria)]
        for row in x
    ]
    best = [max(row[j] for row in normalized) if directions[j] == "benefit"
            else min(row[j] for row in normalized) for j in range(n_criteria)]
    worst = [min(row[j] for row in normalized) if directions[j] == "benefit"
             else max(row[j] for row in normalized) for j in range(n_criteria)]
    scores = []
    for row in normalized:
        distance_best = sqrt(sum((v - b) ** 2 for v, b in zip(row, best)))
        distance_worst = sqrt(sum((v - b) ** 2 for v, b in zip(row, worst)))
        denominator = distance_best + distance_worst
        scores.append(distance_worst / denominator if denominator > 0 else 0.5)
    return tuple(scores)


def demo() -> None:
    decision = DecisionProblem(
        ("Keep", "Lease", "Build"), ("Low", "Base", "High"), (0.25, 0.50, 0.25),
        ((90., 120., 145.), (55., 175., 260.), (-60., 205., 390.)),
    )
    signal = value_of_sample_information(
        decision, ((0.8, 0.2), (0.5, 0.5), (0.2, 0.8)), acquisition_cost=5
    )
    ahp = ahp_priorities(((1, 2, 6), (1 / 2, 1, 3), (1 / 6, 1 / 3, 1)))
    alternatives = ((8, 2, 0.8), (6, 4, 0.9), (7, 3, 0.85))
    scores = topsis_scores(alternatives, ahp.weights, ("benefit", "cost", "benefit"))
    print("Best expected-value decision:", best_expected_action(decision))
    print("EVPI / EVSI / net EVSI:", round(signal.evpi, 3), round(signal.evsi, 3),
          round(signal.net_value, 3))
    print("AHP criteria weights / CR:", ahp.weights, round(ahp.consistency_ratio, 4))
    print("TOPSIS scores:", scores)
    print("Scenario screening:", deep_uncertainty_profiles(
        decision.actions, decision.states, decision.payoffs, aspiration=100
    ))


if __name__ == "__main__":
    demo()
