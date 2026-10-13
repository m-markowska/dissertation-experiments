#!/usr/bin/env python3
"""Require annotations and structured documentation for release functions."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_tree(source_root: Path) -> list[str]:
    """Find functions without annotations or structured documentation.

    Args:
        source_root: Directory containing Python source files to inspect.

    Returns:
        Human-readable failures containing file, line, and function name.
    """
    failures = []
    for path in sorted(source_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(node) or ""
            if node.returns is None:
                failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: {node.name} missing return annotation")
            unannotated = [
                argument.arg
                for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                if argument.arg not in {"self", "cls"} and argument.annotation is None
            ]
            if unannotated:
                failures.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: {node.name} missing annotations for {', '.join(unannotated)}"
                )
            if not doc.strip() or "Args:" not in doc or "Returns:" not in doc:
                failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: {node.name}")
                continue
            args_section = doc.partition("Args:")[2].partition("Returns:")[0]
            parameters = [
                argument.arg
                for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                if argument.arg not in {"self", "cls"}
            ]
            missing = [
                name for name in parameters
                if not re.search(rf"^\s*{re.escape(name)}\s*:", args_section, re.MULTILINE)
            ]
            if missing:
                failures.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: {node.name} missing Args for {', '.join(missing)}"
                )
    return failures


def main() -> int:
    """Check the CanTIERr-2 package and report documentation gaps.

    Args:
        None.

    Returns:
        Zero when every function is documented, otherwise one.
    """
    failures = []
    for source_root in (ROOT / "src", ROOT / "experiments", ROOT / "tools"):
        failures.extend(check_tree(source_root))
    if failures:
        print("Functions missing purpose/Args/Returns documentation:")
        print("\n".join(failures))
        return 1
    print("All release functions have annotations and purpose/Args/Returns documentation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
