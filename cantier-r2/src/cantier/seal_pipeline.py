"""Connect CanTIERr-2 tiers to PRD-SEAL through a canonical 2-ITSL skeleton."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Hashable, Mapping, Optional, Sequence, Set, Tuple

from .learner import CanTierResult, cantier_r2, convert_backpairs

Sym = Hashable
RawExample = Sequence[Any]
Equation = Tuple[list[str], str]
OutputLearner = Callable[[list[Equation], dict[str, set[str]]], Mapping[str, object]]

LEFT_BOUNDARY = ("<",)
RIGHT_BOUNDARY = (">",)
START_STATE = ("<<",)


@dataclass(frozen=True)
class TierTransition:
    """One placeholder-labelled transition in a canonical tier transducer."""

    source: Sym
    symbol: Sym
    placeholder: str
    target: Sym
    identity_output: str


@dataclass(frozen=True)
class TierSealResult:
    """PRD-SEAL output and training evaluation for a fixed learned tier."""

    transitions: Tuple[TierTransition, ...]
    hypothesis: Mapping[str, str]
    equation_count: int
    training_passed: bool
    failures: Tuple[Tuple[int, str, str], ...]


@dataclass(frozen=True)
class CanTierSealResult:
    """Combined tier-inference and transition-output-learning result."""

    tier: CanTierResult
    seal: TierSealResult


def _symbol_text(symbol: Sym) -> str:
    """Return the feature-bundle text stored in a tier symbol.

    Args:
        symbol: Hashable symbol, normally a singleton tuple containing a
            feature-bundle string.

    Returns:
        The singleton tuple value, or ``str(symbol)`` for another shape.
    """
    if isinstance(symbol, tuple) and len(symbol) == 1:
        return str(symbol[0])
    return str(symbol)


def _identity_output(symbol: Sym, right_boundary: Sym) -> str:
    """Return the target-feature identity output for an input symbol.

    Args:
        symbol: Projected input symbol whose first value is the target feature.
        right_boundary: Boundary symbol that produces epsilon.

    Returns:
        Epsilon for the right boundary; otherwise the first feature value.

    Raises:
        ValueError: If a non-boundary symbol has no feature value.
    """
    if symbol == right_boundary:
        return ""
    value = _symbol_text(symbol)
    if not value:
        raise ValueError(f"Cannot derive an identity output from {symbol!r}.")
    return value[0]


def build_canonical_tier_transducer(
    sigma: Set[Sym],
    theta: Set[Sym],
    *,
    left_boundary: Sym = LEFT_BOUNDARY,
    right_boundary: Sym = RIGHT_BOUNDARY,
    start_state: Sym = START_STATE,
) -> list[TierTransition]:
    """Construct the canonical deterministic skeleton for a learned 2-tier.

    Tier symbols update the remembered state, whereas off-tier symbols are
    self-loops. The left boundary enters the machine and the right boundary
    enters the final state. Every transition receives a distinct placeholder
    and an identity-output baseline for PRD-SEAL.

    Args:
        sigma: Observed projected input alphabet, including the right boundary.
        theta: Learned tier alphabet.
        left_boundary: Symbol consumed when entering the machine.
        right_boundary: Symbol consumed when entering the final state.
        start_state: Initial state before the left boundary is consumed.

    Returns:
        Deterministically ordered placeholder-labelled tier transitions.

    Raises:
        ValueError: If the alphabet lacks the right boundary, the tier contains
            an unobserved symbol, or a boundary occurs in the tier.
    """
    alphabet = set(sigma)
    tier = set(theta)
    if right_boundary not in alphabet:
        raise ValueError("The observed alphabet must contain the right boundary.")
    if not tier <= alphabet:
        raise ValueError("Every tier symbol must belong to the observed alphabet.")
    if left_boundary in tier or right_boundary in tier:
        raise ValueError("Boundary symbols cannot belong to the learned tier.")

    ordered_alphabet = sorted(alphabet - {left_boundary}, key=str)
    ordered_states = [left_boundary] + sorted(tier, key=str)
    transitions: list[TierTransition] = []

    def append(source: Sym, symbol: Sym, target: Sym, identity: str) -> None:
        """Append the next sequentially labelled transition.

        Args:
            source: Transition source state.
            symbol: Consumed input symbol.
            target: Transition target state.
            identity: Baseline target-feature output.

        Returns:
            None.
        """
        placeholder = f"O{len(transitions) + 1}"
        transitions.append(
            TierTransition(source, symbol, placeholder, target, identity)
        )

    append(start_state, left_boundary, left_boundary, "")
    for state in ordered_states:
        for symbol in ordered_alphabet:
            if symbol == right_boundary:
                target = right_boundary
            elif symbol in tier:
                target = symbol
            else:
                target = state
            append(
                state,
                symbol,
                target,
                _identity_output(symbol, right_boundary),
            )
    return transitions


def encode_tier_examples(
    examples: Sequence[RawExample],
    transitions: Sequence[TierTransition],
    *,
    start_state: Sym = START_STATE,
) -> list[Equation]:
    """Encode boundary-marked examples as SEAL string equations.

    Args:
        examples: Projected input sequences paired with target-output strings.
        transitions: Canonical placeholder-labelled tier transitions.
        start_state: State used before consuming each input.

    Returns:
        Placeholder paths paired with their required output strings.

    Raises:
        ValueError: If an example does not contain exactly an input and output.
        KeyError: If the skeleton lacks a required state-symbol transition.
    """
    lookup = {
        (transition.source, transition.symbol): (
            transition.placeholder,
            transition.target,
        )
        for transition in transitions
    }
    equations: list[Equation] = []
    for example in examples:
        if len(example) != 2:
            raise ValueError(f"Expected an input-output pair, received {example!r}.")
        input_symbols, output = example
        state = start_state
        path: list[str] = []
        for symbol in input_symbols:
            placeholder, state = lookup[(state, symbol)]
            path.append(placeholder)
        equations.append((path, str(output)))
    return equations


def _singleton_output(value: object) -> str:
    """Normalize one learned SEAL assignment to a string.

    Args:
        value: String or singleton output domain returned by SEAL.

    Returns:
        The sole learned output string.

    Raises:
        ValueError: If the learned assignment is not a string or singleton
            collection.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, (set, frozenset, list, tuple)) and len(value) == 1:
        return str(next(iter(value)))
    raise ValueError(f"Expected one learned output value, received {value!r}.")


def evaluate_tier_hypothesis(
    equations: Sequence[Equation],
    hypothesis: Mapping[str, str],
) -> Tuple[bool, Tuple[Tuple[int, str, str], ...]]:
    """Evaluate a learned transition-output hypothesis on its equations.

    Args:
        equations: Placeholder paths and expected output strings.
        hypothesis: Learned string output for every transition placeholder.

    Returns:
        A success flag and tuples containing the one-based example index,
        expected output, and produced output for every failure.
    """
    failures = []
    for index, (path, expected) in enumerate(equations, start=1):
        produced = "".join(hypothesis[placeholder] for placeholder in path)
        if produced != expected:
            failures.append((index, expected, produced))
    return not failures, tuple(failures)


def learn_tier_seal(
    examples: Sequence[RawExample],
    sigma: Set[Sym],
    theta: Set[Sym],
    *,
    output_learner: Optional[OutputLearner] = None,
) -> TierSealResult:
    """Learn outputs on a canonical 2-tier skeleton with PRD-SEAL.

    Args:
        examples: Boundary-marked projected input-output pairs.
        sigma: Observed projected input alphabet, including the right boundary.
        theta: Tier content supplied by CanTIERr-2.
        output_learner: SEAL-compatible solver. When omitted, the public
            ``seal.learn_prd_seal`` implementation is imported.

    Returns:
        The skeleton, learned output hypothesis, equation count, and complete
        training-sample evaluation.

    Raises:
        ImportError: If the SEAL package is unavailable.
        ValueError: If SEAL does not return one output per placeholder.
    """
    if output_learner is None:
        try:
            from seal import learn_prd_seal
        except ImportError as error:
            raise ImportError(
                "The SEAL package is required for tier-output learning. "
                "Install the sibling equational-learner package first."
            ) from error
        output_learner = learn_prd_seal

    transitions = build_canonical_tier_transducer(sigma, theta)
    equations = encode_tier_examples(examples, transitions)
    identity_hypothesis = {
        transition.placeholder: {transition.identity_output}
        for transition in transitions
    }
    learned = output_learner(equations, deepcopy(identity_hypothesis))
    hypothesis = {
        placeholder: _singleton_output(value)
        for placeholder, value in learned.items()
    }
    passed, failures = evaluate_tier_hypothesis(equations, hypothesis)
    return TierSealResult(
        transitions=tuple(transitions),
        hypothesis=hypothesis,
        equation_count=len(equations),
        training_passed=passed,
        failures=failures,
    )


def learn_cantier_seal(
    examples: Sequence[RawExample],
    *,
    verbose: bool = False,
    output_learner: Optional[OutputLearner] = None,
) -> CanTierSealResult:
    """Infer a tier with CanTIERr-2 and learn its outputs with PRD-SEAL.

    Args:
        examples: Boundary-marked projected input-output pairs.
        verbose: Whether CanTIERr-2 prints its elimination trace.
        output_learner: Optional SEAL-compatible solver passed to
            :func:`learn_tier_seal`.

    Returns:
        The CanTIERr-2 result and the evaluated PRD-SEAL result.
    """
    sample = convert_backpairs(examples, strip_right=False)
    tier_result = cantier_r2(sample, verbose=verbose)
    seal_result = learn_tier_seal(
        examples,
        tier_result.Sigma,
        tier_result.theta,
        output_learner=output_learner,
    )
    return CanTierSealResult(tier=tier_result, seal=seal_result)
