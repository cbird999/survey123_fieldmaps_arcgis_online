"""Default paths and spatial reference for schema builds."""

from __future__ import annotations

from pathlib import Path

# WGS 84 — portable default for AGOL-oriented workflows; override via CLI/env as needed.
DEFAULT_SR_WKID = 4326

# Default output next to package when running examples (override with --gdb).
_DEFAULT_NAME = "VegMon_Schema.gdb"


def default_gdb_path() -> Path:
    """Suggested GDB path under the schema_builder directory (for local trials)."""
    root = Path(__file__).resolve().parent.parent
    return root / _DEFAULT_NAME
