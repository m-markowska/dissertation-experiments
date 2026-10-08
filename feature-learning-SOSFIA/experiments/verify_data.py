#!/usr/bin/env python3
"""Regenerate every feature-pair table and compare it with the repository."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from prepare_features import convert_pairs

ROOT = Path(__file__).resolve().parents[1]

CONFIGS = {
    "english": (
        "english/pairs_segments.tsv",
        "english/inventory_input.tsv",
        "english/inventory_output.tsv",
        "english/pairs_features.tsv",
    ),
    "yawelmani": (
        "yawelmani/pairs_segments.tsv",
        "yawelmani/inventory.tsv",
        "yawelmani/inventory.tsv",
        "yawelmani/pairs_features.tsv",
    ),
    "chukchi": (
        "chukchi/pairs_segments.tsv",
        "chukchi/inventory_input.tsv",
        "chukchi/inventory_output.tsv",
        "chukchi/pairs_features.tsv",
    ),
    **{
        f"polish{size}": (
            f"polish/pairs_segments_{size}.tsv",
            f"polish/inventory_{size}.tsv",
            f"polish/inventory_{size}.tsv",
            f"polish/pairs_features_{size}.tsv",
        )
        for size in (7, 8, 9, 10)
    },
}


def checksum(path: Path) -> str:
    """Return the SHA-256 checksum of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify() -> list[dict[str, object]]:
    """Regenerate all configured data and return comparison records."""
    records = []
    with tempfile.TemporaryDirectory(prefix="fxf-sosfia-data-") as directory:
        temporary = Path(directory)
        for name, (pairs, input_inventory, output_inventory, expected) in CONFIGS.items():
            generated = temporary / f"{name}.tsv"
            expected_path = ROOT / "data" / expected
            count = convert_pairs(
                ROOT / "data" / pairs,
                generated,
                ROOT / "data" / input_inventory,
                ROOT / "data" / output_inventory,
            )
            records.append(
                {
                    "condition": name,
                    "exact_match": generated.read_bytes() == expected_path.read_bytes(),
                    "feature_pairs": count,
                    "sha256": checksum(generated),
                }
            )
    return records


def main() -> int:
    """Verify data, optionally save the structured verification report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()
    records = verify()
    for record in records:
        result = "exact match" if record["exact_match"] else "DIFFERS"
        print(f"{record['condition']:<10} {result:<11} {record['feature_pairs']:>6} pairs")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote verification report to {args.output}")
    return 0 if all(record["exact_match"] for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
