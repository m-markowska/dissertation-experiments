#!/usr/bin/env python3
"""Reproduce the Polish CHILDES incremental ten-fold experiment."""

from __future__ import annotations

import argparse
import csv
import math
import random
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

from seal import learn_seal
from seal.data import extract_feat_pairs, feature_id, read_org_data
from seal.preprocessing import features as inventory_features

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/polish_childes"
REFERENCE_BY_BATCH = {
    batch_size: ROOT / (
        "results/pol-5000-fixed-spec-R2L-identity-incremental-"
        f"learning-curve-batch-{batch_size}.tsv"
    )
    for batch_size in (10, 100)
}


def is_identity_pair(pair: Sequence[Any]) -> bool:
    """Determine whether a full-feature pair preserves its input bundles.

    Args:
        pair: Parsed feature-pair row containing input bundles and outputs.

    Returns:
        True when every output feature string reconstructs the input bundles.
    """
    left, right = pair
    bundles = [item[0] for item in left if item and item[0] not in {"<", ">"}]
    if not bundles:
        return not right
    reconstructed = [
        "".join(bundle[index] for bundle in bundles)
        for index in range(len(bundles[0]))
    ]
    return reconstructed == list(right)


def split_indices(indices: Sequence[int], folds: int) -> list[list[int]]:
    """Split shuffled indexes into balanced consecutive chunks.

    Args:
        indices: Shuffled row indexes.
        folds: Number of chunks to create.

    Returns:
        Fold chunks whose sizes differ by at most one.
    """
    base, remainder = divmod(len(indices), folds)
    chunks = []
    start = 0
    for fold in range(folds):
        size = base + (fold < remainder)
        chunks.append(list(indices[start:start + size]))
        start += size
    return chunks


def stratified_folds(pairs: list[Any], folds: int, seed: int) -> list[tuple[list[int], list[int]]]:
    """Create strict identity-stratified folds with ordered training rows.

    Args:
        pairs: Full dataset in frequency order.
        folds: Number of test partitions.
        seed: Seed used to assign both pair classes to folds.

    Returns:
        ``(train_indexes, test_indexes)`` for each fold. Both index lists retain
        source frequency order after test membership has been selected.
    """
    rng = random.Random(seed)
    identity = [index for index, pair in enumerate(pairs) if is_identity_pair(pair)]
    changed = [index for index, pair in enumerate(pairs) if not is_identity_pair(pair)]
    rng.shuffle(identity)
    rng.shuffle(changed)
    identity_folds = split_indices(identity, folds)
    changed_folds = split_indices(changed, folds)
    assignments = []
    for fold in range(folds):
        test_set = set(identity_folds[fold]) | set(changed_folds[fold])
        train = [index for index in range(len(pairs)) if index not in test_set]
        test = [index for index in range(len(pairs)) if index in test_set]
        assignments.append((train, test))
    return assignments


def fixed_spec(base: str) -> tuple[list[str], int]:
    """Return the fixed Polish feature specification for one target.

    Args:
        base: Target feature name.

    Returns:
        Ordered input features and locality width reported in the dissertation.
    """
    if base == "high":
        return ["high", "nasal", "round", "tap", "voice"], 3
    if base == "tense":
        return ["tense", "nasal", "round", "tap", "voice"], 3
    if base == "voice":
        return ["voice", "son"], 2
    return [base], 1


def checkpoint_sizes(train_total: int, batch_size: int, maximum: int | None) -> list[int]:
    """Build cumulative sample sizes for an incremental fold.

    Args:
        train_total: Number of rows available for training.
        batch_size: Distance between regular checkpoints.
        maximum: Optional last sample size for a partial run.

    Returns:
        Sorted checkpoints beginning at one and including the effective limit.
    """
    limit = train_total if maximum is None else min(train_total, maximum)
    sizes = [1] if limit else []
    sizes.extend(range(batch_size, limit + 1, batch_size))
    if limit and limit not in sizes:
        sizes.append(limit)
    return sorted(set(sizes))


def write_pairs(path: Path, pairs: Sequence[Any]) -> None:
    """Write feature pairs in the learner's Python-literal TSV format.

    Args:
        path: Destination file.
        pairs: Parsed rows to serialize.

    Returns:
        None.
    """
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerows([[repr(cell) for cell in pair] for pair in pairs])


def learn_checkpoint(
    train_path: Path,
    inventory: Path,
    targets: Sequence[str],
) -> dict[str, tuple[str, dict[str, Any]]]:
    """Learn every fixed R2L PRD-SEAL specification at one checkpoint.

    Args:
        train_path: Feature-pair file containing the cumulative R2L prefix.
        inventory: Polish segment-feature inventory.
        targets: Target features to learn.

    Returns:
        Training status and learner details keyed by target feature.
    """
    learned = {}
    for target in targets:
        specification, k = fixed_spec(target)
        status, details = learn_seal(
            specification,
            str(inventory),
            str(inventory),
            str(train_path),
            k,
            direction="R2L",
            check_training=False,
            mode="prd-seal",
        )
        learned[target] = (status, details)
    return learned


def evaluate_feature(
    target: str,
    learned: tuple[str, dict[str, Any]],
    test_rows: list[Any],
    inventory: Path,
) -> tuple[bool, set[int], bool]:
    """Evaluate one learned feature mapping on a held-out fold.

    Args:
        target: Output feature being evaluated.
        learned: Training status and details from :func:`learn_checkpoint`.
        test_rows: Full-feature R2L held-out rows.
        inventory: Polish segment-feature inventory.

    Returns:
        ``(passed, failed_rows, evaluable)``. Row numbers are one-based and
        follow the historical deduplicated-projection evaluation convention.
    """
    status, details = learned
    if status != "passed" or not isinstance(details, dict) or "fst" not in details:
        return False, set(), False
    specification, _k = fixed_spec(target)
    projected = extract_feat_pairs(specification, feature_id(str(inventory)), test_rows)
    fst = details["fst"]
    failed = {
        row_number
        for row_number, (left, expected) in enumerate(projected, start=1)
        if fst.process_input_feature_prod(left)[0] != expected
    }
    return not failed, failed, True


def evaluate_checkpoint(
    learned: dict[str, tuple[str, dict[str, Any]]],
    test_rows: list[Any],
    selected_train_rows: list[Any],
    inventory: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Combine feature evaluations into dissertation learning-curve metrics.

    Args:
        learned: Learned mappings keyed by target feature.
        test_rows: Full-feature R2L held-out rows.
        selected_train_rows: Cumulative R2L training prefix.
        inventory: Polish segment-feature inventory.

    Returns:
        A metric dictionary and detailed failed-pair rows.
    """
    failed_by_row: dict[int, list[str]] = defaultdict(list)
    failed_features = []
    unevaluable = []
    feature_passed = 0
    for target, result in learned.items():
        passed, failed_rows, evaluable = evaluate_feature(target, result, test_rows, inventory)
        if passed:
            feature_passed += 1
        else:
            failed_features.append(target)
        if not evaluable:
            unevaluable.append(target)
        for row_number in failed_rows:
            failed_by_row[row_number].append(target)

    pair_failed = len(failed_by_row)
    pair_total = len(test_rows)
    details = [
        {
            "row_in_test_file": row_number,
            "pair_type": "identical" if is_identity_pair(test_rows[row_number - 1]) else "non_identical",
            "failed_features": ",".join(sorted(features)),
        }
        for row_number, features in sorted(failed_by_row.items())
    ]
    feature_total = len(learned)
    succeeded = feature_passed == feature_total and pair_failed == 0 and not unevaluable
    return {
        "non_identical_training_pairs_seen": sum(
            not is_identity_pair(pair) for pair in selected_train_rows
        ),
        "feature_passed": feature_passed,
        "feature_total": feature_total,
        "feature_accuracy": "" if not feature_total else feature_passed / feature_total,
        "failed_features": ",".join(sorted(failed_features)),
        "pair_passed": pair_total - pair_failed,
        "pair_total": pair_total,
        "pair_accuracy": "" if not pair_total or unevaluable else (pair_total - pair_failed) / pair_total,
        "pair_failed": pair_failed,
        "unevaluable_features": ",".join(sorted(unevaluable)),
        "succeeded": succeeded,
    }, details


def run_fold(
    fold_number: int,
    train_rows: list[Any],
    test_rows: list[Any],
    inventory: Path,
    targets: Sequence[str],
    batch_size: int,
    maximum: int | None,
    temporary: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Run cumulative learning checkpoints for one Polish fold.

    Args:
        fold_number: One-based fold number.
        train_rows: R2L training rows in frequency order.
        test_rows: R2L held-out rows in frequency order.
        inventory: Polish segment-feature inventory.
        targets: Target features to learn.
        batch_size: Distance between regular checkpoints.
        maximum: Optional final checkpoint for a partial run.
        temporary: Directory for the overwritten cumulative training file.

    Returns:
        Fold summary, learning-curve rows, and failed-pair count rows.
    """
    curve = []
    failure_counts = []
    train_path = temporary / f"fold-{fold_number}-r2l.tsv"
    succeeded_at = None
    nonidentity_at_success = None
    for sample_size in checkpoint_sizes(len(train_rows), batch_size, maximum):
        selected = train_rows[:sample_size]
        write_pairs(train_path, selected)
        learned = learn_checkpoint(train_path, inventory, targets)
        metrics, failures = evaluate_checkpoint(learned, test_rows, selected, inventory)
        row = {
            "fold": f"{fold_number}-of-10",
            "sample_size": sample_size,
            "train_total": len(train_rows),
            "test_total": len(test_rows),
            "failed_pairs_path": "",
            **metrics,
        }
        curve.append(row)
        failure_counts.append({
            "fold": row["fold"],
            "sample_size": sample_size,
            "failed_pair_count": len(failures),
            "failed_identical_count": sum(item["pair_type"] == "identical" for item in failures),
            "failed_non_identical_count": sum(item["pair_type"] == "non_identical" for item in failures),
            "failed_features": ",".join(sorted({
                feature
                for item in failures
                for feature in item["failed_features"].split(",")
                if feature
            })),
            "unevaluable_features": metrics["unevaluable_features"],
        })
        print(
            f"fold={fold_number}/10 sample={sample_size} "
            f"features={metrics['feature_passed']}/{metrics['feature_total']} "
            f"pairs={metrics['pair_passed']}/{metrics['pair_total']}",
            flush=True,
        )
        if metrics["succeeded"]:
            succeeded_at = sample_size
            nonidentity_at_success = metrics["non_identical_training_pairs_seen"]
            break

    summary = {
        "fold": f"{fold_number}-of-10",
        "result": "passed" if succeeded_at is not None else "failed",
        "num_datapoints_needed": "" if succeeded_at is None else succeeded_at,
        "num_non_identical_datapoints_needed": (
            "" if nonidentity_at_success is None else nonidentity_at_success
        ),
        "train_total": len(train_rows),
        "test_total": len(test_rows),
        "batches_tried": ",".join(str(row["sample_size"]) for row in curve),
        "needed_non_identical_reversed_segment_path": "",
    }
    return summary, curve, failure_counts


def mean_and_sd(values: Sequence[float]) -> tuple[float | str, float | str]:
    """Compute the arithmetic mean and sample standard deviation.

    Args:
        values: Numeric observations.

    Returns:
        Mean and sample standard deviation, or empty strings for no values.
    """
    numeric = [float(value) for value in values if value != ""]
    if not numeric:
        return "", ""
    mean = sum(numeric) / len(numeric)
    if len(numeric) == 1:
        return mean, 0.0
    variance = sum((value - mean) ** 2 for value in numeric) / (len(numeric) - 1)
    return mean, math.sqrt(variance)


def aggregate_rows(curve: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate learning-curve metrics across observed folds.

    Args:
        curve: Per-fold checkpoint rows.

    Returns:
        One mean-and-standard-deviation row per sample size.
    """
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in curve:
        grouped[int(row["sample_size"])].append(row)
    result = []
    for sample_size in sorted(grouped):
        rows = grouped[sample_size]
        mean_pair, sd_pair = mean_and_sd([row["pair_accuracy"] for row in rows])
        mean_feature, sd_feature = mean_and_sd([row["feature_accuracy"] for row in rows])
        mean_nonidentity, sd_nonidentity = mean_and_sd([
            row["non_identical_training_pairs_seen"] for row in rows
        ])
        result.append({
            "sample_size": sample_size,
            "n_folds_observed": len(rows),
            "mean_pair_accuracy": mean_pair,
            "sd_pair_accuracy": sd_pair,
            "mean_feature_accuracy": mean_feature,
            "sd_feature_accuracy": sd_feature,
            "mean_non_identical_training_pairs_seen": mean_nonidentity,
            "sd_non_identical_training_pairs_seen": sd_nonidentity,
        })
    return result


def write_table(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    """Write dictionaries to a tab-separated result table.

    Args:
        path: Destination table.
        rows: Result dictionaries.
        fields: Column names and output order.

    Returns:
        None.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def verify_reference(curve: Sequence[dict[str, Any]], reference: Path) -> None:
    """Compare generated checkpoint metrics with preserved reference results.

    Args:
        curve: Generated per-fold checkpoint rows.
        reference: Preserved dissertation-result TSV.

    Returns:
        None.

    Raises:
        AssertionError: If a generated metric differs from the reference.
    """
    with reference.open(encoding="utf-8", newline="") as stream:
        expected = {
            (row["fold"], int(row["sample_size"])): row
            for row in csv.DictReader(stream, delimiter="\t")
        }
    fields = (
        "non_identical_training_pairs_seen", "feature_passed", "feature_total",
        "failed_features", "pair_passed", "pair_total", "pair_failed",
        "unevaluable_features", "succeeded",
    )
    for row in curve:
        key = (str(row["fold"]), int(row["sample_size"]))
        if key not in expected:
            raise AssertionError(f"No reference row for {key}.")
        for field in fields:
            if str(row[field]) != expected[key][field]:
                raise AssertionError(
                    f"Reference mismatch at {key}, {field}: "
                    f"generated={row[field]!r}, expected={expected[key][field]!r}"
                )


def run(
    folds: Sequence[int],
    seed: int,
    batch_size: int,
    maximum: int | None,
    output_dir: Path,
    verify: bool,
) -> None:
    """Run selected Polish folds and write dissertation-format tables.

    Args:
        folds: One-based fold numbers to run.
        seed: Stratified-fold assignment seed.
        batch_size: Distance between cumulative checkpoints.
        maximum: Optional final checkpoint for partial verification.
        output_dir: Directory receiving generated tables.
        verify: Whether to compare generated checkpoints with stored results.

    Returns:
        None.
    """
    inventory = DATA / "inventory.tsv"
    forward = read_org_data(str(DATA / "pairs_features_l2r.tsv"))
    reverse = read_org_data(str(DATA / "pairs_features_r2l.tsv"))
    if len(forward) != 5003 or len(reverse) != len(forward):
        raise ValueError("The Polish experiment requires 5,003 aligned pairs.")
    assignments = stratified_folds(forward, 10, seed)
    targets = inventory_features(str(inventory))
    summaries = []
    curve = []
    failed_counts = []
    with tempfile.TemporaryDirectory(prefix="seal-polish-") as temporary_name:
        temporary = Path(temporary_name)
        for fold_number in folds:
            train_indexes, test_indexes = assignments[fold_number - 1]
            train_rows = [reverse[index] for index in train_indexes]
            test_rows = [reverse[index] for index in test_indexes]
            summary, fold_curve, fold_counts = run_fold(
                fold_number, train_rows, test_rows, inventory, targets,
                batch_size, maximum, temporary,
            )
            summaries.append(summary)
            curve.extend(fold_curve)
            failed_counts.extend(fold_counts)
    if verify:
        if batch_size not in REFERENCE_BY_BATCH:
            raise ValueError(
                "Reference verification is available only for batch sizes 10 and 100."
            )
        verify_reference(curve, REFERENCE_BY_BATCH[batch_size])

    prefix = "pol-5000-fixed-spec-R2L-identity-incremental"
    write_table(
        output_dir / f"{prefix}-kfold-summary-batch-{batch_size}-learning-curve-run.tsv",
        summaries,
        ("fold", "result", "num_datapoints_needed", "num_non_identical_datapoints_needed",
         "train_total", "test_total", "batches_tried", "needed_non_identical_reversed_segment_path"),
    )
    write_table(
        output_dir / f"{prefix}-learning-curve-batch-{batch_size}.tsv",
        curve,
        ("fold", "sample_size", "non_identical_training_pairs_seen", "train_total",
         "test_total", "feature_passed", "feature_total", "feature_accuracy",
         "failed_features", "pair_passed", "pair_total", "pair_accuracy",
         "pair_failed", "unevaluable_features", "failed_pairs_path", "succeeded"),
    )
    write_table(
        output_dir / f"{prefix}-learning-curve-batch-{batch_size}-failed-pair-counts.tsv",
        failed_counts,
        ("fold", "sample_size", "failed_pair_count", "failed_identical_count",
         "failed_non_identical_count", "failed_features", "unevaluable_features"),
    )
    write_table(
        output_dir / f"{prefix}-learning-curve-batch-{batch_size}-aggregate.tsv",
        aggregate_rows(curve),
        ("sample_size", "n_folds_observed", "mean_pair_accuracy", "sd_pair_accuracy",
         "mean_feature_accuracy", "sd_feature_accuracy",
         "mean_non_identical_training_pairs_seen", "sd_non_identical_training_pairs_seen"),
    )
    print(f"wrote Polish experiment tables to {output_dir}")


def main() -> int:
    """Parse command-line options and run the Polish experiment.

    Args:
        None.

    Returns:
        Zero after all selected folds and checks complete.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fold", type=int, action="append", choices=range(1, 11))
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--max-sample", type=int)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/polish-rerun")
    parser.add_argument("--verify-reference", action="store_true")
    args = parser.parse_args()
    run(args.fold or list(range(1, 11)), args.seed, args.batch_size, args.max_sample,
        args.output_dir, args.verify_reference)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
