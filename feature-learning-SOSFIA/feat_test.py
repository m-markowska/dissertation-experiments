#!/usr/bin/env python3
"""Run one feature-learning AMSSA experiment."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from fxf_sosfia import FST_feature, convert_data, extract_feat_pairs
from fxf_sosfia import preprocessing, rules
from fxf_sosfia.sample_search import minimal_sample_feat

ROOT = Path(__file__).resolve().parent

CONFIGS = {
    "english": ("english/inventory_input.tsv", "english/inventory_output.tsv", "english/pairs_features.tsv", 2, "nasalize"),
    "yawelmani": ("yawelmani/inventory.tsv", "yawelmani/inventory.tsv", "yawelmani/pairs_features.tsv", 3, "shorten_vowel"),
    "chukchi": ("chukchi/inventory_input.tsv", "chukchi/inventory_output.tsv", "chukchi/pairs_features.tsv", 3, "schwa_epen"),
    "polish7": ("polish/inventory_7.tsv", "polish/inventory_7.tsv", "polish/pairs_features_7.tsv", 3, "o_raise_devoice_new"),
}


def reverse_data(data):
    """Reverse feature pairs while retaining the boundary markers."""
    return [
        ([pair[0][0], *pair[0][1:-1][::-1], pair[0][-1]], [value[::-1] for value in pair[1]])
        for pair in data
    ]


def run(language, direction, k_mode, feature, batch_size, seed):
    """Run AMSSA for one feature specification."""
    sigma_name, delta_name, pairs_name, gold_k, rule_name = CONFIGS[language]
    sigma_path = ROOT / "data" / sigma_name
    delta_path = ROOT / "data" / delta_name
    pairs_path = ROOT / "data" / pairs_name
    sigma = preprocessing.sigma(str(sigma_path))
    delta = preprocessing.delta(str(delta_path))
    identity = preprocessing.transitions_gen(sigma, gold_k, str(sigma_path))
    if direction == "R2L":
        rule_name = rule_name.replace("_new", "") + "_reverse"
    gold = getattr(rules, rule_name)(sigma, identity, gold_k, str(sigma_path))
    data = convert_data(str(pairs_path))
    if direction == "R2L":
        data = reverse_data(data)
    fst = FST_feature(
        preprocessing.states_gen(sigma, gold_k), sigma, delta, "<<", ">", gold,
        preprocessing.features(str(sigma_path)),
    )
    random.seed(seed)
    current_k = gold_k if k_mode == "fixed" else 1
    while True:
        projected = extract_feat_pairs(feature, preprocessing.feature_id(str(sigma_path)), data, current_k)
        result = minimal_sample_feat(
            feature, projected, data, fst, str(sigma_path), str(delta_path),
            current_k, batch_size=batch_size,
        )
        if result != "More data" or k_mode == "fixed":
            return current_k, result
        current_k += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=CONFIGS, default="english")
    parser.add_argument("--direction", choices=("L2R", "R2L"), default="L2R")
    parser.add_argument("--k-mode", choices=("fixed", "learned"), default="learned")
    parser.add_argument("--feature", nargs="+", default=["nasal", "cons"])
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    learned_k, result = run(
        args.language, args.direction, args.k_mode, args.feature,
        args.batch_size, args.seed,
    )
    if result == "More data":
        raise SystemExit("No sufficient sample was found at the fixed k.")
    candidates = result if isinstance(result, list) else [result]
    print(f"direction: {args.direction}")
    print(f"k: {learned_k}")
    for candidate in candidates:
        print(f"feature: {candidate[0][0]}")
        print(f"selected sample size: {candidate[0][1]}")


if __name__ == "__main__":
    main()
