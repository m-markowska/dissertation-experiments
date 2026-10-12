#!/usr/bin/env python3
"""Convert reconstructed CSV pairs into segment and feature TSV files."""

from __future__ import annotations

import argparse
import ast
import csv
import unicodedata
from pathlib import Path

ALIASES = {"č": "t͡ʃ", "y": "j"}


def normalize_symbol(symbol: str, aliases: dict[str, str] | None = None) -> str:
    """Normalize Unicode and apply transcription aliases used in the sources.

    Args:
        symbol: Source transcription symbol.
        aliases: Optional source-to-experiment symbol replacements.

    Returns:
        NFC-normalized symbol used by the experiment inventories.
    """
    normalized = unicodedata.normalize("NFC", symbol)
    return (aliases or {}).get(normalized, normalized)


def read_inventory(path: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Read a segment-feature inventory.

    Args:
        path: TSV inventory whose columns are segments and rows are features.

    Returns:
        Ordered feature names and a mapping from segments to feature values.
    """
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    features = [row[0] for row in rows[1:]]
    segments = [unicodedata.normalize("NFC", item) for item in rows[0][1:]]
    mapping = {segment: [row[index + 1] for row in rows[1:]] for index, segment in enumerate(segments)}
    return features, mapping


def csv_to_segment_pairs(source: Path, destination: Path, aliases: dict[str, str] | None = None) -> int:
    """Convert a reconstructed UR/SR CSV to boundary-marked segment pairs.

    Args:
        source: CSV with space-separated UR and SR strings in its first two columns.
        destination: TSV path to create.
        aliases: Replacements applied while creating the segment representation.

    Returns:
        Number of pairs written.
    """
    count = 0
    with source.open(encoding="utf-8-sig", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.reader(src)
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            inp = [normalize_symbol(token, aliases) for token in row[0].split()]
            out = [normalize_symbol(token, aliases) for token in row[1].split()]
            writer.writerow([repr([("<",)] + [(token,) for token in inp] + [(">",)]), repr(out)])
            count += 1
    return count


def inventory_values(symbol: str, inventory: dict[str, list[str]]) -> list[str]:
    """Look up a segment bundle, applying known source notation aliases.

    Args:
        symbol: Segment symbol written in the pair file.
        inventory: Segment-to-feature mapping loaded from an inventory TSV.

    Returns:
        Ordered feature values for the requested segment.
    """
    normalized = unicodedata.normalize("NFC", symbol)
    candidate = normalized if normalized in inventory else ALIASES.get(normalized, normalized)
    try:
        return inventory[candidate]
    except KeyError as error:
        raise ValueError(f"Segment {symbol!r} is absent from the feature inventory.") from error


def segments_to_features(segment_path: Path, destination: Path, input_inventory: Path, output_inventory: Path) -> int:
    """Convert segment pairs to full feature-bundle pairs.

    Args:
        segment_path: TSV containing boundary-marked input segments and output segments.
        destination: Feature-pair TSV path to create.
        input_inventory: Inventory used to encode input segments.
        output_inventory: Inventory used to encode output segments.

    Returns:
        Number of feature pairs written.
    """
    input_features, input_map = read_inventory(input_inventory)
    output_features, output_map = read_inventory(output_inventory)
    if input_features != output_features:
        raise ValueError("Input and output inventories must use the same ordered feature rows.")
    count = 0
    with segment_path.open(encoding="utf-8", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.reader(src, delimiter="\t")
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        for left_raw, right_raw in reader:
            left = ast.literal_eval(left_raw)
            right = ast.literal_eval(right_raw)
            encoded_left = [("<",)] + [
                ("".join(inventory_values(item[0], input_map)),)
                for item in left[1:-1]
            ] + [(">",)]
            output_columns = [inventory_values(item, output_map) for item in right]
            encoded_right = ["".join(column) for column in zip(*output_columns)] if output_columns else []
            writer.writerow([repr(encoded_left), repr(encoded_right)])
            count += 1
    return count


def reverse_feature_pairs(source: Path, destination: Path) -> int:
    """Reverse feature inputs and per-feature output strings for R2L learning.

    Args:
        source: Forward feature-pair TSV.
        destination: Reversed feature-pair TSV to create.

    Returns:
        Number of reversed pairs written.
    """
    count = 0
    with source.open(encoding="utf-8", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.reader(src, delimiter="\t")
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        for left_raw, right_raw in reader:
            left = ast.literal_eval(left_raw)
            right = ast.literal_eval(right_raw)
            reversed_left = [left[0]] + left[1:-1][::-1] + [left[-1]]
            writer.writerow([repr(reversed_left), repr([value[::-1] for value in right])])
            count += 1
    return count


def reverse_segment_pairs(source: Path, destination: Path) -> int:
    """Reverse segment inputs and outputs for right-to-left processing.

    Args:
        source: Forward segment-pair TSV.
        destination: Reversed segment-pair TSV to create.

    Returns:
        Number of reversed pairs written.
    """
    count = 0
    with source.open(encoding="utf-8", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.reader(src, delimiter="\t")
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        for left_raw, right_raw in reader:
            left = ast.literal_eval(left_raw)
            right = ast.literal_eval(right_raw)
            reversed_left = [left[0]] + left[1:-1][::-1] + [left[-1]]
            writer.writerow([repr(reversed_left), repr(right[::-1])])
            count += 1
    return count


def main() -> int:
    """Parse paths and regenerate all three prepared formats.

    Args:
        None.

    Returns:
        Zero after successful conversion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("input_inventory", type=Path)
    parser.add_argument("output_inventory", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--segment-alias", action="append", default=[], metavar="SOURCE=TARGET")
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    segment = args.output_directory / "pairs_segments.tsv"
    forward = args.output_directory / "pairs_features_l2r.tsv"
    reverse = args.output_directory / "pairs_features_r2l.tsv"
    aliases = dict(item.split("=", 1) for item in args.segment_alias)
    count = csv_to_segment_pairs(args.source_csv, segment, aliases)
    segments_to_features(segment, forward, args.input_inventory, args.output_inventory)
    reverse_feature_pairs(forward, reverse)
    print(f"wrote {count} pairs to {args.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
