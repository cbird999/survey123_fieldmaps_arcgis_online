"""CLI: build vegetation monitoring schema (or list layer names)."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from vegqc_schema.builder import build_domains, build_feature_class, ensure_file_gdb
from vegqc_schema.config import DEFAULT_SR_WKID, default_gdb_path
from vegqc_schema.registry import SCHEMAS, resolve_schema


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _select_layers(feature_classes: list[dict], names: list[str] | None) -> list[dict]:
    if not names:
        return list(feature_classes)
    by_name = {s["name"]: s for s in feature_classes}
    missing = [n for n in names if n not in by_name]
    if missing:
        available = ", ".join(sorted(by_name))
        raise SystemExit(f"Unknown layer(s): {missing}. Available: {available}")
    return [by_name[n] for n in names]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build feature classes in a file geodatabase from registered schemas (requires arcpy / ArcGIS Pro).",
    )
    parser.add_argument(
        "--schema",
        default="vegetation",
        choices=sorted(SCHEMAS.keys()),
        help="Registered schema package to build (default: vegetation).",
    )
    parser.add_argument(
        "--gdb",
        type=Path,
        default=None,
        help=f"Path to .gdb (created if missing). Default: {default_gdb_path()}",
    )
    parser.add_argument(
        "--wkid",
        type=int,
        default=DEFAULT_SR_WKID,
        help=f"Spatial reference WKID for new feature classes (default: {DEFAULT_SR_WKID}).",
    )
    parser.add_argument(
        "--layers",
        nargs="*",
        metavar="NAME",
        default=None,
        help="Feature class base names to build (default: all layers in the selected schema).",
    )
    parser.add_argument(
        "--overwrite-gdb",
        action="store_true",
        help="Delete and recreate the entire geodatabase if it exists.",
    )
    parser.add_argument(
        "--overwrite-layers",
        action="store_true",
        help="Replace feature classes that already exist (GDB left intact).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print defined layer names and exit.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    _setup_logging(args.verbose)

    domains, feature_classes = resolve_schema(args.schema)

    if args.list:
        for spec in feature_classes:
            print(f"{spec['name']}\t{spec['geometry']}")
        return 0

    gdb = args.gdb or default_gdb_path()
    layers = _select_layers(feature_classes, args.layers)

    if args.overwrite_gdb:
        ensure_file_gdb(gdb, overwrite=True)
    else:
        ensure_file_gdb(gdb, overwrite=False)

    gdb_str = str(gdb.resolve())
    build_domains(gdb_str, domains)

    for spec in layers:
        build_feature_class(
            gdb_str,
            spec,
            spatial_reference_wkid=args.wkid,
            overwrite=args.overwrite_layers,
        )

    logging.getLogger(__name__).info("Done: %s", gdb_str)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
