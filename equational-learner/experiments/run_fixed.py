#!/usr/bin/env python3
"""Run a documented fixed SEAL feature specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from seal import learn_seal

ROOT = Path(__file__).resolve().parents[1]

PRESETS = {
    "serbo_croatian_lat": {
        "features": ["cons", "lat"], "inventory": "serbo_croatian/inventory.tsv",
        "l2r": "serbo_croatian/pairs_features_l2r.tsv", "r2l": "serbo_croatian/pairs_features_r2l.tsv", "k": 3,
    },
    "polish_voice": {
        "features": ["voice", "son"], "inventory": "polish_childes/inventory.tsv",
        "l2r": "polish_childes/pairs_features_l2r.tsv", "r2l": "polish_childes/pairs_features_r2l.tsv", "k": 2,
    },
    "polish_high": {
        "features": ["high", "nasal", "round", "tap", "voice"], "inventory": "polish_childes/inventory.tsv",
        "l2r": "polish_childes/pairs_features_l2r.tsv", "r2l": "polish_childes/pairs_features_r2l.tsv", "k": 3,
    },
    "polish_tense": {
        "features": ["tense", "nasal", "round", "tap", "voice"], "inventory": "polish_childes/inventory.tsv",
        "l2r": "polish_childes/pairs_features_l2r.tsv", "r2l": "polish_childes/pairs_features_r2l.tsv", "k": 3,
    },
}


def to_json(value: Any) -> Any:
    """Convert learner objects and containers to JSON-compatible values.

    Args:
        value: Arbitrary learner result value.

    Returns:
        A JSON scalar, list, or dictionary representing ``value``.
    """
    if isinstance(value, dict):
        return {str(key): to_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "transitions"):
        return {"type": type(value).__name__, "transitions": to_json(value.transitions)}
    return repr(value)


def run(preset: str, direction: str, mode: str) -> dict:
    """Learn and evaluate one preset configuration.

    Args:
        preset: Name of a configuration in ``PRESETS``.
        direction: Processing direction, ``L2R`` or ``R2L``.
        mode: SEAL output-distribution mode, ``prd-seal`` or ``lcd-seal``.

    Returns:
        Dictionary containing the configuration, status, and learned result.
    """
    config = PRESETS[preset]
    inventory = ROOT / "data" / config["inventory"]
    data = ROOT / "data" / config[direction.lower()]
    status, details = learn_seal(
        config["features"], str(inventory), str(inventory), str(data), config["k"],
        direction=direction, mode=mode,
    )
    return {
        "preset": preset, "direction": direction, "mode": mode,
        "features": config["features"], "k": config["k"],
        "status": status, "details": to_json(details),
    }


def main() -> int:
    """Parse CLI options, run the learner, and write JSON output.

    Args:
        None.

    Returns:
        Zero for a training-consistent hypothesis and one for failure.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="serbo_croatian_lat")
    parser.add_argument("--direction", choices=("L2R", "R2L"), default="L2R")
    parser.add_argument(
        "--mode",
        choices=("prd-seal", "lcd-seal"),
        default="lcd-seal",
        help="SEAL output-distribution mode.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.preset, args.direction, args.mode)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
