#!/usr/bin/env python3
"""Require purpose, argument, and return documentation for package functions."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_tree(source_root: Path) -> list[str]:
    """Find functions without complete structured documentation.

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
    """Check the FxF(SOSFIA) package and report documentation gaps.

    Args:
        None.

    Returns:
        Zero when every function is documented, otherwise one.
    """
    failures = check_tree(ROOT / "src/fxf_sosfia")
    if failures:
        print("Functions missing purpose/Args/Returns documentation:")
        print("\n".join(failures))
        return 1
    print("All core functions have purpose, Args, and Returns documentation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
