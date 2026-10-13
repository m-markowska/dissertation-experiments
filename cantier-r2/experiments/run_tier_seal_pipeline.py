#!/usr/bin/env python3
"""Learn tiers and their transition outputs for configured projections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cantier import learn_cantier_seal
from cantier.data import project_pairs

from experiment_config import (
    ExperimentSpec,
    load_experiment_spec,
    select_configurations,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "data/turkish/chapter7_experiments.json"


def _symbol_json(symbol: object) -> list[str]:
    """Convert a transducer symbol to a JSON list.

    Args:
        symbol: Tuple-wrapped symbol or another printable state value.

    Returns:
        Symbol components represented as strings.
    """
    if isinstance(symbol, tuple):
        return [str(item) for item in symbol]
    return [str(symbol)]


def run(
    spec: ExperimentSpec,
    targets: list[str] | None = None,
    verbose: bool = False,
) -> dict[str, dict[str, object]]:
    """Learn tiers and transition outputs for selected projections.

    Args:
        spec: Dataset paths and named ordered feature projections.
        targets: Configuration names to run, or ``None`` to run all of them.
        verbose: Whether to print CanTIERr-2 elimination details.

    Returns:
        JSON-compatible tier, transducer, SEAL, and evaluation results.
    """
    results: dict[str, dict[str, object]] = {}
    for target in select_configurations(spec, targets):
        features = spec.configurations[target]
        projected = project_pairs(spec.pairs, spec.inventory, features)
        combined = learn_cantier_seal(projected, verbose=verbose)
        baseline = {
            transition.placeholder: transition.identity_output
            for transition in combined.seal.transitions
        }
        changed = []
        for transition in combined.seal.transitions:
            learned_output = combined.seal.hypothesis[transition.placeholder]
            if learned_output != baseline[transition.placeholder]:
                changed.append(
                    {
                        "placeholder": transition.placeholder,
                        "source": _symbol_json(transition.source),
                        "input": _symbol_json(transition.symbol),
                        "identity_output": transition.identity_output,
                        "learned_output": learned_output,
                        "target": _symbol_json(transition.target),
                    }
                )
        results[target] = {
            "features": features,
            "sample_size": len(projected),
            "theta": [
                _symbol_json(symbol)
                for symbol in sorted(combined.tier.theta, key=str)
            ],
            "transition_count": len(combined.seal.transitions),
            "changed_transitions": changed,
            "training_examples_correct": (
                combined.seal.equation_count - len(combined.seal.failures)
            ),
            "training_examples_total": combined.seal.equation_count,
            "training_passed": combined.seal.training_passed,
        }
    return results


def main() -> int:
    """Parse options, run the combined experiment, and render JSON.

    Args:
        None.

    Returns:
        Zero when every selected condition passes, otherwise one.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--target", action="append")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        spec = load_experiment_spec(args.config)
        results = run(spec, args.target, args.verbose)
    except ValueError as error:
        parser.error(str(error))
    rendered = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")
    return 0 if all(result["training_passed"] for result in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
