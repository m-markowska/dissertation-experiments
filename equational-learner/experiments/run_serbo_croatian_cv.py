#!/usr/bin/env python3
"""Reproduce the fixed-specification Serbo-Croatian 5-fold evaluation."""

from __future__ import annotations

import argparse
import csv
import random
import tempfile
from pathlib import Path
from typing import Any

from seal import learn_seal
from seal.data import extract_feat_pairs, feature_id, read_org_data

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/serbo_croatian"


def is_identity_pair(pair: Any) -> bool:
    """Classify whether a full-feature pair preserves every input bundle.

    Args:
        pair: Parsed input and feature-major output pair.

    Returns:
        True when reconstructing the outputs yields the input bundles.
    """
    left, right = pair
    bundles = [item[0] for item in left if item and item[0] not in {"<", ">"}]
    if not bundles:
        return not right
    return ["".join(bundle[index] for bundle in bundles) for index in range(len(bundles[0]))] == right


def split_indices(indices: list[int], folds: int) -> list[list[int]]:
    """Divide an ordered index list into balanced consecutive fold chunks.

    Args:
        indices: Row indexes to distribute.
        folds: Number of output chunks.

    Returns:
        Ordered fold chunks whose sizes differ by at most one.
    """
    base, remainder = divmod(len(indices), folds)
    result = []
    start = 0
    for index in range(folds):
        size = base + (index < remainder)
        result.append(indices[start:start + size])
        start += size
    return result


def stratified_folds(pairs: list[Any], folds: int, seed: int) -> list[tuple[list[int], list[int]]]:
    """Create reproducible folds balanced across identity and changed pairs.

    Args:
        pairs: Full feature-pair examples in their stored order.
        folds: Number of train/test partitions.
        seed: Random seed for shuffling both strata and each partition.

    Returns:
        Train and test row indexes for each fold.
    """
    rng = random.Random(seed)
    identical = [index for index, pair in enumerate(pairs) if is_identity_pair(pair)]
    changed = [index for index, pair in enumerate(pairs) if not is_identity_pair(pair)]
    rng.shuffle(identical)
    rng.shuffle(changed)
    identical_folds = split_indices(identical, folds)
    changed_folds = split_indices(changed, folds)
    result = []
    for fold in range(folds):
        test_set = set(identical_folds[fold]) | set(changed_folds[fold])
        train = [index for index in range(len(pairs)) if index not in test_set]
        test = list(test_set)
        rng.shuffle(train)
        rng.shuffle(test)
        result.append((train, test))
    return result


def write_pairs(path: Path, pairs: list[Any]) -> None:
    """Write parsed pair data in the Python-literal TSV format used by SEAL.

    Args:
        path: Destination TSV path.
        pairs: Parsed feature-pair rows to serialize.

    Returns:
        None; the destination file contains one serialized pair per row.
    """
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerows([[repr(cell) for cell in pair] for pair in pairs])


def project_examples(
    pairs: list[Any],
    features: list[str],
    target: str,
    inventory: Path,
) -> list[tuple[list[tuple[str, ...]], str]]:
    """Project examples using the dissertation experiment's deduplication rule.

    Args:
        pairs: Full feature-pair examples in the requested direction.
        features: Input features selected by the fixed specification.
        target: Output feature predicted by this specification.
        inventory: TSV inventory defining feature order.
    Returns:
        Unique projected input/output pairs in first-occurrence order.
    """
    if not features or features[0] != target:
        raise ValueError("The target feature must be first in the specification.")
    return extract_feat_pairs(features, feature_id(str(inventory)), pairs)


def read_specs(
    path: Path,
    requested: list[str] | None,
    target_features: list[str] | None,
) -> list[dict[str, str]]:
    """Read fixed feature specifications, optionally filtering by spec set.

    Args:
        path: TSV containing target features, feature bundles, and k values.
        requested: Optional list of specification-set names to run.
        target_features: Optional target feature names to run.

    Returns:
        Selected specification rows in their recorded order.
    """
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return [
        row for row in rows
        if (requested is None or row["spec_set"] in requested)
        and (target_features is None or row["target_feature"] in target_features)
    ]


def evaluate_spec(
    spec: dict[str, str],
    fold_number: int,
    train_rows: list[Any],
    test_rows: list[Any],
    direction: str,
    inventory: Path,
) -> dict[str, Any]:
    """Train one fixed specification and evaluate its held-out feature pairs.

    Args:
        spec: Fixed target feature, selected features, and memory bound.
        fold_number: One-based held-out fold identifier.
        train_rows: Full feature pairs assigned to training.
        test_rows: Full feature pairs assigned to evaluation.
        direction: Learning direction, either ``L2R`` or ``R2L``.
        inventory: Input and output feature inventory for this language.

    Returns:
        Metrics and statuses for the training and held-out feature projection.
    """
    features = [value for value in spec["features"].split(",") if value]
    k = int(spec["k"])
    with tempfile.TemporaryDirectory(prefix="seal-serbo-fold-") as temporary:
        train_path = Path(temporary) / "train.tsv"
        write_pairs(train_path, train_rows)
        train_status, details = learn_seal(
            features, str(inventory), str(inventory), str(train_path), k,
            direction=direction, check_training=True, mode="lcd-seal",
        )
        if train_status != "passed":
            return {
                "train_status": train_status, "heldout_status": "not_evaluated",
                "passed": 0, "total": len(test_rows), "accuracy": "",
                "failed_rows": list(range(len(test_rows))),
            }
        projected = project_examples(test_rows, features, spec["target_feature"], inventory)
        fst = details["fst"]
        outcomes = [fst.process_input_feature_prod(left)[0] == right for left, right in projected]
        status = "passed" if all(outcomes) else "failed"
        passed = sum(outcomes)
        total = len(projected)
        return {
            "train_status": train_status,
            "heldout_status": status,
            "passed": passed,
            "total": total,
            "accuracy": f"{passed / total:.6f}" if total else "",
            "failed_rows": [index for index, outcome in enumerate(outcomes) if not outcome],
        }


def run(
    folds: int,
    seed: int,
    selected_sets: list[str] | None,
    target_features: list[str] | None,
    output: Path,
) -> int:
    """Run all selected Serbo-Croatian specifications and write a TSV summary.

    Args:
        folds: Number of stratified folds.
        seed: Seed controlling the fold assignment.
        selected_sets: Optional specification-set names to run.
        target_features: Optional target features to run.
        output: Summary TSV path to create.

    Returns:
        Number of specification, fold, and direction evaluations written.
    """
    inventory = DATA / "inventory.tsv"
    forward = read_org_data(str(DATA / "pairs_features_l2r.tsv"))
    reverse = read_org_data(str(DATA / "pairs_features_r2l.tsv"))
    if len(forward) != len(reverse):
        raise ValueError("Forward and reverse data must have the same number of rows.")
    assignments = stratified_folds(forward, folds, seed)
    specs = read_specs(DATA / "fixed_specs.tsv", selected_sets, target_features)
    fields = [
        "spec_set", "fold", "direction", "target_feature", "features", "k",
        "train_status", "heldout_status", "heldout_passed", "heldout_total", "heldout_accuracy",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    pair_failures: dict[tuple[str, str, str], set[int]] = {}
    pair_test_sizes: dict[tuple[str, str, str], int] = {}
    for fold_index, (train_indices, test_indices) in enumerate(assignments, start=1):
        for direction, data in (("L2R", forward), ("R2L", reverse)):
            train = [data[index] for index in train_indices]
            test = [data[index] for index in test_indices]
            for spec in specs:
                metrics = evaluate_spec(spec, fold_index, train, test, direction, inventory)
                key = (spec["spec_set"], f"{fold_index}-of-{folds}", direction)
                pair_failures.setdefault(key, set()).update(metrics["failed_rows"])
                pair_test_sizes[key] = len(test)
                summary_rows.append({
                    "spec_set": spec["spec_set"], "fold": key[1],
                    "direction": direction, "target_feature": spec["target_feature"],
                    "features": spec["features"], "k": spec["k"],
                    "train_status": metrics["train_status"],
                    "heldout_status": metrics["heldout_status"],
                    "heldout_passed": metrics["passed"], "heldout_total": metrics["total"],
                    "heldout_accuracy": metrics["accuracy"],
                })
    for row in summary_rows:
        key = (row["spec_set"], row["fold"], row["direction"])
        total = pair_test_sizes[key]
        failed = len(pair_failures[key])
        passed = total - failed
        row["selected_specs_pair_passed"] = passed
        row["selected_specs_pair_total"] = total
        row["selected_specs_pair_accuracy"] = f"{passed / total:.6f}" if total else ""
    fields += ["selected_specs_pair_passed", "selected_specs_pair_total", "selected_specs_pair_accuracy"]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)
    return len(summary_rows)


def main() -> int:
    """Parse options and run the configured cross-validation experiment.

    Args:
        None.

    Returns:
        Zero after writing the result summary.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--spec-set", action="append")
    parser.add_argument("--target-feature", action="append")
    parser.add_argument("--output", type=Path, default=ROOT / "results/serbo-croatian-fixed-spec-cv.tsv")
    args = parser.parse_args()
    count = run(args.folds, args.seed, args.spec_set, args.target_feature, args.output)
    print(f"wrote {count} evaluations to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
