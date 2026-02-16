"""Spotlight CLI.

This module provides headless commands that don't require launching Pygame.

Currently supported:
- validate: validate a tasks JSON file and exit with status code.

Contract
- Inputs:
  - argv / CLI flags
  - task file path
- Outputs:
  - exit code 0 on success
  - exit code 2 on validation/load error
  - exit code 1 on unexpected internal error
- Side effects:
  - reads a JSON file from disk
  - prints human-readable messages to stdout/stderr
"""

from __future__ import annotations

import argparse
import sys

from src.services.task_loader import TaskLoader, TaskLoadError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spotlight", description="Spotlight CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a tasks JSON file")
    validate.add_argument(
        "--task-file",
        default="data/tasks.json",
        help="Path to tasks JSON file (default: data/tasks.json)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Returns an exit code instead of calling sys.exit directly to keep this testable.
    """

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        try:
            tasks = TaskLoader.load_tasks(args.task_file)
        except TaskLoadError as e:
            print(f"INVALID: {e}", file=sys.stderr)
            return 2
        except Exception as e:
            # Defensive: never raise from CLI main
            print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
            return 1

        print(f"OK: {len(tasks)} tasks loaded from {args.task_file}")
        return 0

    # Should not be reachable due to required=True on subparsers
    print("ERROR: Unknown command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

