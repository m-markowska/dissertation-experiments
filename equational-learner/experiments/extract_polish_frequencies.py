#!/usr/bin/env python3
"""Rebuild the curated Polish frequency table from its Excel workbook."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
HEADER = [
    "inflected form",
    "inflected form occurances",
    "base form",
    "base form occurances",
]


def shared_strings(archive: ZipFile) -> list[str]:
    """Read shared text values used by cells in the workbook.

    Args:
        archive: Open Excel workbook ZIP archive.

    Returns:
        Shared string values in workbook index order.
    """
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(text.text or "" for text in item.iter(f"{{{MAIN_NS}}}t"))
        for item in root
    ]


def cell_values(archive: ZipFile, sheet_name: str, strings: list[str]) -> dict[int, dict[str, str]]:
    """Read worksheet cell values keyed by row number and column letter.

    Args:
        archive: Open Excel workbook ZIP archive.
        sheet_name: Worksheet XML path within the workbook archive.
        strings: Shared string table used by the workbook.

    Returns:
        Row-number mapping of column letters to decoded cell values.
    """
    root = ET.fromstring(archive.read(sheet_name))
    rows: dict[int, dict[str, str]] = {}
    for row in root.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row"):
        values: dict[str, str] = {}
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            reference = cell.attrib["r"]
            column = "".join(char for char in reference if char.isalpha())
            value_node = cell.find(f"{{{MAIN_NS}}}v")
            value = "" if value_node is None else value_node.text or ""
            if cell.attrib.get("t") == "s" and value:
                value = strings[int(value)]
            values[column] = value
        rows[int(row.attrib["r"])] = values
    return rows


def extract_frequency_table(workbook: Path, manifest: Path, destination: Path) -> int:
    """Recreate selected workbook rows as a frequency table.

    Args:
        workbook: Source workbook with Occurances and Frequencies sheets.
        manifest: TSV containing selected ``frequencies_sheet_row`` values.
        destination: Frequency TSV path to create.

    Returns:
        Number of selected rows written.
    """
    with ZipFile(workbook) as archive:
        strings = shared_strings(archive)
        source_rows = cell_values(archive, "xl/worksheets/sheet1.xml", strings)
        frequency_rows = cell_values(archive, "xl/worksheets/sheet2.xml", strings)
        total = float(source_rows[4]["G"])

    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        selected = [
            int(row["frequencies_sheet_row"])
            for row in csv.DictReader(stream, delimiter="\t")
        ]

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        for row_number in selected:
            row = frequency_rows[row_number]
            writer.writerow([
                row["A"],
                f"{float(row['B']) * total:.2f}",
                row["C"],
                f"{float(row['D']) * total:.2f}",
            ])
    return len(selected)


def main() -> int:
    """Parse CLI paths and write the curated Polish frequency table.

    Args:
        None.

    Returns:
        Zero after successful extraction.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    count = extract_frequency_table(args.workbook, args.manifest, args.destination)
    print(f"wrote {count} curated rows to {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
