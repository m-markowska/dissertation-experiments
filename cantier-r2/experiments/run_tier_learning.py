#!/usr/bin/env python3
"""Learn tiers for feature projections defined in an experiment file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cantier import cantier_r2, convert_backpairs
from cantier.data import project_pairs

from experiment_config import (
    ExperimentSpec,
    load_experiment_spec,
    select_configurations,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "data/turkish/chapter7_experiments.json"


def run(
    spec: ExperimentSpec,
    targets: list[str] | None = None,
    verbose: bool = False,
) -> dict[str, dict[str, object]]:
    """Infer tiers for selected dataset feature projections.

    Args:
        spec: Dataset paths and named ordered feature projections.
        targets: Configuration names to run, or ``None`` to run all of them.
        verbose: Whether to print each CanTIERr-2 elimination step.

    Returns:
        JSON-compatible tier and alphabet information by configuration.
    """
    results: dict[str, dict[str, object]] = {}
    for target in select_configurations(spec, targets):
        features = spec.configurations[target]
        projected = project_pairs(spec.pairs, spec.inventory, features)
        sample = convert_backpairs(projected, strip_right=False)
        learned = cantier_r2(sample, verbose=verbose)
        results[target] = {
            "features": features,
            "sample_size": len(sample),
            "theta": [list(symbol) for symbol in sorted(learned.theta, key=str)],
            "sigma": [list(symbol) for symbol in sorted(learned.Sigma, key=str)],
        }
    return results


def main() -> int:
    """Parse CLI options, learn tiers, and optionally write JSON.

    Args:
        None.

    Returns:
        Zero after all requested configurations complete.
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
