#!/usr/bin/env python3
"""Run the dissertation's full-sample experiments for five languages."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Sequence

from seal import learn_seal

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CONFIG = {
    "koasati": {"inventory": "inventory_union.tsv", "mode": "prd-seal"},
    "kerewe": {"inventory": "inventory.tsv", "mode": "prd-seal"},
    "lumasaaba": {"inventory": "inventory_union.tsv", "mode": "prd-seal"},
    "samoan": {"inventory": "inventory.tsv", "mode": "lcd-seal"},
    "serbo_croatian": {"inventory": "inventory.tsv", "mode": "lcd-seal"},
}


def read_specs(language: str) -> list[dict[str, str]]:
    """Read the recorded full-sample specifications for one language.

    Args:
        language: Dataset directory and configuration name.

    Returns:
        Specification rows in target-feature order. For Serbo-Croatian, only
        rows in the dissertation's ``final`` set are returned.
    """
    path = DATA / language / "fixed_specs.tsv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return [row for row in rows if row.get("spec_set", "final") == "final"]


def expected_passes(language: str, direction: str) -> int:
    """Return the recorded number of successful feature specifications.

    Args:
        language: Dataset configuration name.
        direction: ``L2R`` or ``R2L``.

    Returns:
        Expected successful specifications out of 25.
    """
    if language == "lumasaaba" and direction == "L2R":
        return 20
    return 25


def run_language(language: str, directions: Sequence[str]) -> list[dict[str, Any]]:
    """Run all fixed specifications for one language.

    Args:
        language: Dataset configuration name.
        directions: Learning directions to evaluate.

    Returns:
        One status row per target feature and direction.
    """
    config = CONFIG[language]
    directory = DATA / language
    inventory = directory / config["inventory"]
    rows = []
    for direction in directions:
        pair_path = directory / f"pairs_features_{direction.lower()}.tsv"
        for spec in read_specs(language):
            feature_names = [name for name in spec["features"].split(",") if name]
            status, details = learn_seal(
                feature_names,
                str(inventory),
                str(inventory),
                str(pair_path),
                int(spec["k"]),
                direction=direction,
                mode=config["mode"],
            )
            rows.append({
                "language": language,
                "direction": direction,
                "mode": config["mode"],
                "target_feature": spec["target_feature"],
                "features": spec["features"],
                "k": spec["k"],
                "status": status,
                "message": details.get("eval_msg", details.get("error_msg", ""))
                if isinstance(details, dict) else str(details),
            })
    return rows


def summarize(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize feature-level statuses by language and direction.

    Args:
        rows: Feature-level experiment results.

    Returns:
        Passed, total, expected-passed, and match status for each condition.
    """
    conditions = sorted({(row["language"], row["direction"]) for row in rows})
    summary = []
    for language, direction in conditions:
        selected = [
            row for row in rows
            if row["language"] == language and row["direction"] == direction
        ]
        passed = sum(row["status"] == "passed" for row in selected)
        expected = expected_passes(language, direction)
        summary.append({
            "language": language,
            "direction": direction,
            "passed": passed,
            "total": len(selected),
            "expected_passed": expected,
            "matches_dissertation": passed == expected,
        })
    return summary


def write_table(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    """Write experiment rows as a tab-separated table.

    Args:
        path: Destination TSV path.
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


def run(languages: Sequence[str], directions: Sequence[str], output: Path) -> bool:
    """Run selected full-sample experiments and write results.

    Args:
        languages: Dataset configuration names.
        directions: Learning directions to evaluate.
        output: Feature-level result table.

    Returns:
        True when every condition matches its recorded success count.
    """
    rows = []
    for language in languages:
        rows.extend(run_language(language, directions))
    summary = summarize(rows)
    write_table(
        output,
        rows,
        ("language", "direction", "mode", "target_feature", "features", "k", "status", "message"),
    )
    summary_path = output.with_name(f"{output.stem}-summary{output.suffix}")
    write_table(
        summary_path,
        summary,
        ("language", "direction", "passed", "total", "expected_passed", "matches_dissertation"),
    )
    for row in summary:
        print(
            f"{row['language']} {row['direction']}: "
            f"{row['passed']}/{row['total']} "
            f"(expected {row['expected_passed']})",
            flush=True,
        )
    print(f"wrote feature results to {output}")
    print(f"wrote condition summary to {summary_path}")
    return all(row["matches_dissertation"] for row in summary)


def main() -> int:
    """Parse command-line options and run the full-sample experiments.

    Args:
        None.

    Returns:
        Zero when recorded counts are reproduced, otherwise one.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", action="append", choices=sorted(CONFIG))
    parser.add_argument("--direction", action="append", choices=("L2R", "R2L"))
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "results/textbook-full-sample-rerun.tsv",
    )
    args = parser.parse_args()
    matched = run(args.language or list(CONFIG), args.direction or ["L2R", "R2L"], args.output)
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
