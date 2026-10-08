#!/usr/bin/env python3
"""Extract the SOSFIA result tables from a text rendering of Appendix B.

Create the input with Ghostscript, for example:

    gs -q -dNOPAUSE -dBATCH -sDEVICE=txtwrite \
      -sOutputFile=/tmp/dissertation.txt dissertation.pdf
    python tools/extract_appendix_b.py /tmp/dissertation.txt

The dissertation PDF is not distributed with this repository.  The checked-in
TSV files are the authoritative transcription; this script documents how that
transcription was produced and checks each summary against its ten source runs.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from pathlib import Path


FEATURES = {
    "english": [
        "nasal+cons", "high", "low", "tense", "front", "back", "round",
        "long", "cons", "son", "cont", "delrel", "approx", "voice", "lab",
        "labdent", "cor", "ant", "distr", "strid", "lat", "dor",
    ],
    "yawelmani": [
        "high", "low", "tense", "front", "back", "round", "long", "cons",
        "son", "cont", "delrel", "nasal", "approx", "voice", "lab",
        "labdent", "cor", "ant", "distr", "strid", "lat", "dor",
        "constrgl", "spreadgl",
    ],
    "chukchi": [
        "high", "low", "tense", "front", "back", "round+high", "long",
        "cons", "son+low", "cont+tense", "delrel+long", "approx", "nasal+son",
        "voice+cons", "lab", "labdent", "cor", "ant+labdent", "distr+cor",
        "strid+dor", "lat", "dor",
    ],
    "polish": [
        "voice+son", "son", "cons", "cont", "cor", "ant", "dor", "lab",
        "distr", "delrel", "nasal", "lat", "high+voice+son+low", "back",
        "low", "tense+voice+son+round", "round",
    ],
}

# Yawelmani's summary tables put ``approx`` before ``nasal``, unlike the raw
# ten-run tables. The other languages retain their raw-table order.
SUMMARY_FEATURES = {
    **FEATURES,
    "yawelmani": [
        "high", "low", "tense", "front", "back", "round", "long", "cons",
        "son", "cont", "delrel", "approx", "nasal", "voice", "lab",
        "labdent", "cor", "ant", "distr", "strid", "lat", "dor",
        "constrgl", "spreadgl",
    ],
}

# table: (language, direction, k mode, k value, alphabet size)
RAW_TABLES = {
    1: ("english", "left-to-right", "fixed", "2", "26"),
    2: ("english", "right-to-left", "fixed", "2", "26"),
    3: ("english", "left-to-right", "learned", "", "26"),
    4: ("english", "right-to-left", "learned", "", "26"),
    13: ("yawelmani", "left-to-right", "fixed", "3", "7"),
    14: ("yawelmani", "right-to-left", "fixed", "3", "7"),
    15: ("yawelmani", "left-to-right", "learned", "", "7"),
    16: ("yawelmani", "right-to-left", "learned", "", "7"),
    25: ("chukchi", "left-to-right", "fixed", "3", "7"),
    26: ("chukchi", "right-to-left", "fixed", "3", "7"),
    27: ("chukchi", "left-to-right", "learned", "", "7"),
    28: ("chukchi", "right-to-left", "learned", "", "7"),
    37: ("polish", "left-to-right", "fixed", "3", "7"),
    38: ("polish", "right-to-left", "fixed", "3", "7"),
    39: ("polish", "left-to-right", "learned", "", "7"),
    40: ("polish", "right-to-left", "learned", "", "7"),
}

# Summary table to the corresponding ten-run table.
SUMMARY_TABLES = {
    5: 3, 6: 4, 7: 1, 8: 2,
    17: 15, 18: 16, 19: 13, 20: 14,
    29: 27, 30: 28, 31: 25, 32: 26,
    41: 39, 42: 40, 43: 37, 44: 38,
}

GROWTH_TABLES = {
    45: ("polish", "left-to-right", "fixed", "3"),
    46: ("polish", "right-to-left", "fixed", "3"),
    47: ("polish", "left-to-right", "learned", ""),
    48: ("polish", "right-to-left", "learned", ""),
}

NUMBER = re.compile(r"(?<![\d.])\d[\d,]*(?:\.\d+)?")


def numeric_fields(line: str) -> list[str]:
    """Return plain numeric strings, removing thousands separators."""
    return [value.replace(",", "") for value in NUMBER.findall(line)]


def table_rows(lines: list[str], table: int, width: int) -> list[list[str]]:
    """Find the numeric rows immediately preceding an Appendix B caption."""
    caption = next(
        i for i, line in enumerate(lines) if f"TABLE B.{table}:" in line
    )
    header = max(i for i in range(caption) if "Feature set" in lines[i])
    rows = []
    for line in lines[header + 1 : caption]:
        values = numeric_fields(line)
        if len(values) == width:
            rows.append(values)
    if width == 10 and rows and rows[0] == [str(i) for i in range(1, 11)]:
        rows.pop(0)
    return rows


def metadata(table: int, condition: tuple[str, ...]) -> dict[str, str]:
    language, direction, k_mode, k_value, *alphabet = condition
    record = {
        "table_id": f"B.{table}",
        "dissertation_page": str(243 + table),
        "language": language,
        "direction": direction,
        "k_mode": k_mode,
        "k_value": k_value,
    }
    if alphabet:
        record["alphabet_size"] = alphabet[0]
    return record


def extract(lines: list[str]):
    runs = []
    parsed_runs: dict[int, dict[str, list[int]]] = {}
    for table, condition in RAW_TABLES.items():
        language = condition[0]
        labels = FEATURES[language] + ["__synthesized__"]
        rows = table_rows(lines, table, 10)
        if len(rows) != len(labels):
            raise ValueError(
                f"B.{table}: expected {len(labels)} data rows, found {len(rows)}"
            )
        parsed_runs[table] = {}
        for label, values in zip(labels, rows):
            parsed_runs[table][label] = [int(value) for value in values]
            record = metadata(table, condition)
            record.update({
                "feature_set": label,
                "measure": "M_F" if label == "__synthesized__" else "M_phi",
            })
            record.update({f"run_{i}": value for i, value in enumerate(values, 1)})
            runs.append(record)

    summaries = []
    for table, raw_table in SUMMARY_TABLES.items():
        condition = RAW_TABLES[raw_table]
        labels = SUMMARY_FEATURES[condition[0]]
        rows = table_rows(lines, table, 3)
        if len(rows) != len(labels):
            raise ValueError(
                f"B.{table}: expected {len(labels)} data rows, found {len(rows)}"
            )
        for label, values in zip(labels, rows):
            sample_size, stated_mean, stated_sd = values
            source = parsed_runs[raw_table][label]
            calculated_mean = statistics.mean(source)
            calculated_sd = statistics.stdev(source)
            # Appendix B reports integer means and SD to at most two decimals.
            validation_notes = []
            if abs(float(stated_mean) - calculated_mean) > 0.500000001:
                validation_notes.append(
                    f"reported mean differs from B.{raw_table} calculated mean "
                    f"{calculated_mean:g}"
                )
            sd_places = len(stated_sd.partition(".")[2])
            sd_rounding_tolerance = 0.5 * (10 ** -sd_places) + 1e-9
            if abs(float(stated_sd) - calculated_sd) > sd_rounding_tolerance:
                validation_notes.append(
                    f"reported SD differs from B.{raw_table} calculated SD "
                    f"{calculated_sd:g}"
                )
            record = metadata(table, condition)
            record.update({
                "source_runs_table_id": f"B.{raw_table}",
                "feature_set": label,
                "sample_size": sample_size,
                "mean_selected_size": stated_mean,
                "sd": stated_sd,
                "validation_note": "; ".join(validation_notes),
            })
            summaries.append(record)

    growth = []
    for table, condition in GROWTH_TABLES.items():
        labels = FEATURES["polish"] + ["__synthesized__"]
        rows = table_rows(lines, table, 6)
        if len(rows) != len(labels):
            raise ValueError(
                f"B.{table}: expected {len(labels)} data rows, found {len(rows)}"
            )
        for label, values in zip(labels, rows):
            for alphabet_size, offset in (("8", 0), ("9", 2), ("10", 4)):
                record = metadata(table, condition)
                record.update({
                    "alphabet_size": alphabet_size,
                    "feature_set": label,
                    "measure": "M_F" if label == "__synthesized__" else "M_phi",
                    "full_sample_size": values[offset],
                    "selected_sample_size": values[offset + 1],
                })
                growth.append(record)
    return runs, summaries, growth


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", type=Path, help="Ghostscript txtwrite output")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/reference"),
        help="TSV destination (default: results/reference)",
    )
    args = parser.parse_args()
    lines = args.text.read_text(encoding="utf-8", errors="replace").splitlines()
    runs, summaries, growth = extract(lines)

    common = [
        "table_id", "dissertation_page", "language", "direction", "k_mode",
        "k_value", "alphabet_size", "feature_set",
    ]
    write_tsv(
        args.output_dir / "appendix_b_runs.tsv",
        runs,
        common + ["measure"] + [f"run_{i}" for i in range(1, 11)],
    )
    write_tsv(
        args.output_dir / "appendix_b_summaries.tsv",
        summaries,
        common + [
            "source_runs_table_id", "sample_size", "mean_selected_size", "sd",
            "validation_note",
        ],
    )
    write_tsv(
        args.output_dir / "appendix_b_polish_alphabet_growth.tsv",
        growth,
        common + ["measure", "full_sample_size", "selected_sample_size"],
    )
    noted_summaries = sum(bool(row["validation_note"]) for row in summaries)
    print(
        f"Wrote {len(runs)} run rows, {len(summaries)} summary rows, "
        f"and {len(growth)} alphabet-growth rows to {args.output_dir}; "
        f"{noted_summaries} summary rows carry a validation note"
    )


if __name__ == "__main__":
    main()
