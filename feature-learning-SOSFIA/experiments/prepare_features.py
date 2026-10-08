#!/usr/bin/env python3
"""Regenerate an FxF(SOSFIA) feature-pair file from segment pairs."""

from __future__ import annotations

import argparse
import ast
import csv
from pathlib import Path

DEVOICED_FROM = {
    "p": "b", "t": "d", "k": "g", "f": "v", "s": "z",
    "ʂ": "ʐ", "ɕ": "ʑ", "x": "ɣ", "t͡s": "d͡z",
    "t͡ʂ": "d͡ʐ", "t͡ɕ": "d͡ʑ",
}


def read_inventory(path: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Read a feature-by-segment inventory into an ordered lookup.

    Args:
        path: TSV inventory with segments in the header and features in rows.

    Returns:
        Ordered feature names and each segment's ordered feature values.
    """
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    features = [row[0] for row in rows[1:]]
    segments = rows[0][1:]
    mapping = {
        segment: [row[index + 1] for row in rows[1:]]
        for index, segment in enumerate(segments)
    }
    return features, mapping


def convert_pairs(source: Path, destination: Path, input_inventory: Path, output_inventory: Path) -> int:
    """Convert boundary-marked segment pairs to full-feature pairs.

    Args:
        source: Segment TSV with ``Input`` and ``Output`` columns.
        destination: Feature TSV path to create.
        input_inventory: Inventory defining the input segment feature bundles.
        output_inventory: Inventory defining the output segment feature bundles.

    Returns:
        Number of converted pairs.
    """
    features, input_mapping = read_inventory(input_inventory)
    output_features, output_mapping = read_inventory(output_inventory)
    if features != output_features:
        raise ValueError("Input and output inventories must have the same ordered features.")
    if "voice" in features:
        voice_index = features.index("voice")
        for unvoiced, voiced in DEVOICED_FROM.items():
            if unvoiced not in output_mapping and voiced in output_mapping:
                bundle = output_mapping[voiced].copy()
                bundle[voice_index] = "-"
                output_mapping[unvoiced] = bundle
    count = 0
    with source.open(encoding="utf-8-sig", newline="") as src, destination.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.reader(src, delimiter="\t")
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        next(reader, None)
        writer.writerow(["Input", "Output"])
        for left_raw, right_raw in reader:
            left = ast.literal_eval(left_raw)
            right = ast.literal_eval(right_raw)
            encoded_left = [left[0]] + [
                ("".join(input_mapping[item[0]]),) for item in left[1:-1]
            ] + [left[-1]]
            try:
                output_columns = [output_mapping[item] for item in right]
            except KeyError as error:
                raise ValueError(
                    f"Segment {error.args[0]!r} is absent from an input or output inventory."
                ) from error
            encoded_right = [
                "".join(values) for values in zip(*output_columns)
            ] if output_columns else [""] * len(features)
            writer.writerow([repr(encoded_left), repr(encoded_right)])
            count += 1
    return count


def main() -> int:
    """Parse file paths and regenerate a feature-pair TSV.

    Args:
        None.

    Returns:
        Zero after successful conversion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("segment_pairs", type=Path)
    parser.add_argument("input_inventory", type=Path)
    parser.add_argument("output_inventory", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    count = convert_pairs(
        args.segment_pairs, args.destination, args.input_inventory, args.output_inventory
    )
    print(f"wrote {count} feature pairs to {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
