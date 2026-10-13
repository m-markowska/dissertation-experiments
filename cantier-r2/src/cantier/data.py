"""Load prepared feature data and construct CanTIERr-2 projections."""

from __future__ import annotations

import ast
import csv
from pathlib import Path

ProjectedPair = list[object]


def feature_names(inventory: Path) -> list[str]:
    """Read ordered feature names from an inventory.

    Args:
        inventory: TSV feature-inventory path.

    Returns:
        Feature names in row order.
    """
    with inventory.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    return [row[0] for row in rows[1:]]


def read_pairs(path: Path) -> list[tuple[list[tuple[str]], list[str]]]:
    """Read literal-valued feature pairs from a TSV file.

    Args:
        path: Two-column feature-pair TSV.

    Returns:
        Parsed input tuple sequences and feature-major output strings.
    """
    result = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.reader(stream, delimiter="\t"):
            if len(row) >= 2:
                result.append((ast.literal_eval(row[0]), ast.literal_eval(row[1])))
    return result


def project_pairs(path: Path, inventory: Path, selected: list[str]) -> list[ProjectedPair]:
    """Project full feature pairs onto an ordered feature selection.

    Args:
        path: Full feature-pair TSV.
        inventory: Inventory defining feature row positions.
        selected: Features to retain; the first is the predicted output feature.

    Returns:
        First-occurrence-unique pairs whose inputs contain the selected
        bundles and whose output is the string for the first selected feature.

    Raises:
        ValueError: If a selected feature is absent from the inventory.
    """
    names = feature_names(inventory)
    indexes = [names.index(name) for name in selected]
    target_index = indexes[0]
    projected: list[ProjectedPair] = []
    for left, right in read_pairs(path):
        new_left = [("<",)]
        for symbol in left[1:-1]:
            new_left.append(("".join(symbol[0][index] for index in indexes),))
        new_left.append((">",))
        projected.append([new_left, right[target_index]])

    # The dissertation pipeline treats identical pairs produced by projection
    # as one observation and retains their first occurrence.
    unique: list[ProjectedPair] = []
    for pair in projected:
        if pair not in unique:
            unique.append(pair)
    return unique
