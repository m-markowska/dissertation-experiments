#!/usr/bin/env python3
"""Transcribe the frequency-ordered Polish word list into UR/SR segment pairs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from prepare_data import reverse_feature_pairs, reverse_segment_pairs, segments_to_features

RULES = sorted([
    ("dz", "d͡z"), ("dż", "d͡ʐ"), ("dź", "d͡ʑ"), ("cz", "t͡ʂ"), ("sz", "ʂ"), ("rz", "ʐ"), ("ch", "x"),
    ("ą", "ɔ̃"), ("ę", "ɛ̃"), ("ó", "u"), ("ł", "w"), ("ń", "ɲ"), ("ś", "ɕ"), ("ź", "ʑ"), ("ż", "ʐ"), ("ć", "t͡ɕ"),
    ("a", "a"), ("b", "b"), ("c", "t͡s"), ("d", "d"), ("e", "ɛ"), ("f", "f"), ("g", "g"), ("h", "x"),
    ("i", "i"), ("j", "j"), ("k", "k"), ("l", "l"), ("m", "m"), ("n", "n"), ("o", "ɔ"), ("p", "p"),
    ("r", "r"), ("s", "s"), ("t", "t"), ("u", "u"), ("w", "v"), ("y", "ɨ"), ("z", "z"),
], key=lambda pair: len(pair[0]), reverse=True)

FINAL_DEVOICE = {"d": "t", "g": "k", "b": "p", "z": "s", "ʐ": "ʂ", "ʑ": "ɕ", "v": "f", "d͡z": "t͡s", "d͡ʑ": "t͡ɕ", "d͡ʐ": "t͡ʂ"}
O_BEFORE_FINAL = {"d", "g", "b", "dz", "dź", "dż", "j", "ł", "r", "z", "w", "l", "ż", "ź"}
EXCLUDED_FORMS = {"kolor", "włoż", "założ"}


def transcribe(word: str) -> list[str]:
    """Convert Polish spelling to the experiment's segment symbols.

    Args:
        word: Orthographic word form.

    Returns:
        Ordered phonological segment symbols.
    """
    word = word.lower().strip()
    result, index = [], 0
    while index < len(word):
        for source, target in RULES:
            if word.startswith(source, index):
                result.append(target)
                index += len(source)
                break
        else:
            result.append(word[index])
            index += 1
    return result


def underlying(word: str) -> list[str]:
    """Recover the experiment's underlying representation.

    Args:
        word: Orthographic word form.

    Returns:
        Segment list with underlying /ɔ/ restored in raising contexts.
    """
    phones = transcribe(word)
    for ending in sorted(O_BEFORE_FINAL, key=len, reverse=True):
        if word.lower().strip().endswith("ó" + ending):
            phones[-2] = "ɔ"
            break
    return phones


def surface(word: str) -> list[str]:
    """Produce the experiment's surface representation.

    Args:
        word: Orthographic word form.

    Returns:
        Segment list after word-final devoicing.
    """
    phones = transcribe(word)
    normalized = word.lower().strip()
    for ending in sorted(O_BEFORE_FINAL, key=len, reverse=True):
        if normalized.endswith("o" + ending):
            phones[-2] = "u"
            break
    if phones and phones[-1] in FINAL_DEVOICE:
        phones[-1] = FINAL_DEVOICE[phones[-1]]
    return phones


def convert_frequency_list(source: Path, destination: Path) -> int:
    """Convert the frequency list to boundary-marked segment pairs.

    Args:
        source: Tab-separated frequency list with a header and word in column one.
        destination: Segment-pair TSV path to create.

    Returns:
        Number of word pairs written.
    """
    count = 0
    with source.open(encoding="utf-8-sig", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.reader(src, delimiter="\t")
        writer = csv.writer(dst, delimiter="\t", lineterminator="\n")
        next(reader, None)
        for row in reader:
            if not row:
                continue
            word = row[0]
            if word.lower().strip() in EXCLUDED_FORMS:
                continue
            left = [("<",)] + [(phone,) for phone in underlying(word)] + [(">",)]
            writer.writerow([repr(left), repr(surface(word))])
            count += 1
    return count


def main() -> int:
    """Parse CLI paths and write Polish segment pairs.

    Args:
        None.

    Returns:
        Zero after successful conversion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--feature-output", type=Path)
    parser.add_argument("--reverse-segment-output", type=Path)
    parser.add_argument("--reverse-feature-output", type=Path)
    args = parser.parse_args()
    print(f"wrote {convert_frequency_list(args.source, args.destination)} pairs")
    if args.inventory and args.feature_output:
        segments_to_features(args.destination, args.feature_output, args.inventory, args.inventory)
    if args.reverse_segment_output:
        reverse_segment_pairs(args.destination, args.reverse_segment_output)
    if args.feature_output and args.reverse_feature_output:
        reverse_feature_pairs(args.feature_output, args.reverse_feature_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
