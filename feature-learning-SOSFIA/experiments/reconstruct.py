#!/usr/bin/env python3
"""Reconstruct a complete gold mapping from its generated feature pairs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from fxf_sosfia import FST_feature, Sosfia, check_the_difference, convert_data
from fxf_sosfia import preprocessing, rules

ROOT = Path(__file__).resolve().parents[1]

CONFIGS = {
    "english": ("english/inventory_input.tsv", "english/inventory_output.tsv", "english/pairs_features.tsv", 2, "nasalize"),
    "yawelmani": ("yawelmani/inventory.tsv", "yawelmani/inventory.tsv", "yawelmani/pairs_features.tsv", 3, "shorten_vowel"),
    "chukchi": ("chukchi/inventory_input.tsv", "chukchi/inventory_output.tsv", "chukchi/pairs_features.tsv", 3, "schwa_epen"),
    "polish7": ("polish/inventory_7.tsv", "polish/inventory_7.tsv", "polish/pairs_features_7.tsv", 3, "o_raise_devoice_new"),
}


def run(language: str) -> str:
    """Run one full-data reconstruction.

    Args:
        language: Key naming one configuration in ``CONFIGS``.

    Returns:
        The comparison message produced for the gold and learned transitions.
    """
    sigma_name, delta_name, pairs_name, k, rule_name = CONFIGS[language]
    sigma_path = ROOT / "data" / sigma_name
    delta_path = ROOT / "data" / delta_name
    pairs_path = ROOT / "data" / pairs_name
    sigma = preprocessing.sigma(str(sigma_path))
    delta = preprocessing.delta(str(delta_path))
    identity = preprocessing.transitions_gen(sigma, k, str(sigma_path))
    gold = getattr(rules, rule_name)(sigma, identity, k, str(sigma_path))
    states = preprocessing.states_gen(sigma, k)
    features = preprocessing.features(str(sigma_path))
    start = FST_feature(states, sigma, delta, "<<", ">", identity, features)
    learned = Sosfia(convert_data(str(pairs_path)), start, features).fill_in_trans()
    return check_the_difference(gold, learned)


def main() -> int:
    """Parse command-line input and report reconstruction success.

    Args:
        None.

    Returns:
        Zero when the learned transition set matches the gold set, otherwise one.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=sorted(CONFIGS), default="english")
    parser.add_argument("--output", type=Path, help="Optional JSON result path.")
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    start_clock = time.monotonic()
    result = run(args.language)
    duration = time.monotonic() - start_clock
    print(result)
    print(f"elapsed seconds: {duration:.6f}")
    if args.output:
        _, _, pairs_name, k, rule_name = CONFIGS[args.language]
        record = {
            "condition": args.language,
            "duration_seconds": duration,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "k": k,
            "matched_gold": result == "It's a match",
            "pairs_file": pairs_name,
            "result": result,
            "rule": rule_name,
            "started_at_utc": started.isoformat(),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote result to {args.output}")
    return 0 if result == "It's a match" else 1


if __name__ == "__main__":
    raise SystemExit(main())
