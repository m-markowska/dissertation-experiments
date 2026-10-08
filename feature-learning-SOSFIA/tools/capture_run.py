#!/usr/bin/env python3
"""Run an experiment while preserving its terminal output and metadata."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def safe_name(value: str) -> str:
    """Convert a human-readable run name into a filesystem-safe name."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    if not cleaned:
        raise ValueError("Run name must contain at least one letter or number.")
    return cleaned


def package_versions() -> dict[str, str]:
    """Return versions for packages relevant to these experiments."""
    versions = {}
    for distribution in ("fxf-sosfia", "numpy", "pandas"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = "not installed"
    return versions


def git_revision() -> str:
    """Return the checked-out Git revision, if available."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def create_run_directory(parent: Path, name: str, timestamp: str) -> Path:
    """Create a unique directory for one run."""
    candidate = parent / f"{timestamp}-{safe_name(name)}"
    suffix = 2
    while candidate.exists():
        candidate = parent / f"{timestamp}-{safe_name(name)}-{suffix}"
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def write_metadata(path: Path, metadata: dict[str, object]) -> None:
    """Write stable, human-readable JSON metadata."""
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Parse arguments, execute the command, and archive the run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Short experiment name.")
    parser.add_argument("--seed", required=True, type=int, help="Recorded random seed.")
    parser.add_argument("--note", default="", help="Optional description of the run.")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=ROOT / "results" / "runs",
        help="Parent directory for captured runs.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run, normally placed after --.",
    )
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("an experiment command is required after --")

    started = datetime.now(timezone.utc)
    timestamp = started.strftime("%Y%m%dT%H%M%SZ")
    run_directory = create_run_directory(args.results_dir.resolve(), args.name, timestamp)
    metadata_path = run_directory / "metadata.json"
    log_path = run_directory / "terminal.log"
    metadata: dict[str, object] = {
        "command": command,
        "cwd": str(ROOT),
        "git_revision": git_revision(),
        "name": args.name,
        "note": args.note,
        "packages": package_versions(),
        "platform": platform.platform(),
        "python": sys.version,
        "seed": args.seed,
        "started_at_utc": started.isoformat(),
        "status": "running",
    }
    write_metadata(metadata_path, metadata)

    environment = os.environ.copy()
    environment["FXF_SOSFIA_SEED"] = str(args.seed)
    environment["PYTHONHASHSEED"] = str(args.seed)
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = source_path + os.pathsep + environment.get("PYTHONPATH", "")

    start_clock = time.monotonic()
    return_code = 130
    process = None
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            return_code = process.wait()
    except KeyboardInterrupt:
        if process is not None:
            process.terminate()
            process.wait()
        print("\nRun interrupted; partial output was preserved.", file=sys.stderr)
    finally:
        finished = datetime.now(timezone.utc)
        metadata.update(
            {
                "duration_seconds": round(time.monotonic() - start_clock, 6),
                "finished_at_utc": finished.isoformat(),
                "return_code": return_code,
                "status": "completed" if return_code == 0 else "failed",
                "terminal_log": str(log_path),
            }
        )
        write_metadata(metadata_path, metadata)
        print(f"\nCaptured run: {run_directory}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
