#!/usr/bin/env python3
"""Backward-compatible wrapper: same as `promote.py --project vegqc --from DEV --to CERT` (+ your extra flags)."""

from __future__ import annotations

import sys

from promote import main as promote_main


def main() -> int:
    argv = sys.argv[1:]
    if "--project" not in argv:
        argv = ["--project", "vegqc", "--from", "DEV", "--to", "CERT"] + argv
    return promote_main(argv)


if __name__ == "__main__":
    sys.exit(main())
