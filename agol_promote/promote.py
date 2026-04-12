#!/usr/bin/env python3
"""
Promote ArcGIS Online items between environments (same org), config-driven.

Linear default: only the next hop in promotion_chain is allowed (e.g. DEV→CERT→TEST→PROD).
See projects.yaml and README.md.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from promote_core import run_promotion

logger = logging.getLogger("agol_promote")


def _default_config_path() -> Path:
    return Path(__file__).resolve().parent / "projects.yaml"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Clone hosted layers + web maps between AGOL env folders (linear promotion).",
    )
    p.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to projects.yaml (default: alongside this script).",
    )
    p.add_argument(
        "--project",
        required=True,
        metavar="SLUG",
        help="Project key from projects.yaml (e.g. vegqc).",
    )
    p.add_argument(
        "--from",
        dest="from_env",
        required=True,
        metavar="ENV",
        help="Source environment name (e.g. DEV, CERT, TEST).",
    )
    p.add_argument(
        "--to",
        dest="to_env",
        required=True,
        metavar="ENV",
        help="Target environment name (must be the next step after --from unless --allow-nonlinear).",
    )
    p.add_argument("--url", default=None, help="Portal URL (default: AGOL_URL or https://www.arcgis.com)")
    p.add_argument("--profile", default=None, help="ArcGIS API Python profile (or AGOL_PROFILE).")
    p.add_argument(
        "--content-owner",
        default=None,
        metavar="USERNAME",
        help="Owner of source/target folders if not the signed-in user.",
    )
    p.add_argument(
        "--copy-data",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Clone feature data (default: true).",
    )
    p.add_argument(
        "--search-existing-items",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Reuse existing matching items in org (default: false).",
    )
    p.add_argument(
        "--replace",
        action="store_true",
        help="Delete target-titled items in the target folder before cloning.",
    )
    p.add_argument(
        "--allow-nonlinear",
        action="store_true",
        help="Allow any env→env pair listed in promotion_chain (emergency use only).",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    cfg = args.config or _default_config_path()
    if not cfg.is_file():
        logger.error("Config not found: %s", cfg)
        return 2

    url = (args.url or os.environ.get("AGOL_URL") or "https://www.arcgis.com").strip() or "https://www.arcgis.com"

    try:
        run_promotion(
            config_path=cfg,
            project_slug=args.project,
            from_env=args.from_env,
            to_env=args.to_env,
            url=url,
            profile=args.profile,
            content_owner=args.content_owner,
            replace=args.replace,
            dry_run=args.dry_run,
            copy_data=args.copy_data,
            search_existing_items=args.search_existing_items,
            allow_nonlinear=args.allow_nonlinear,
        )
        return 0
    except (LookupError, ValueError) as e:
        logger.error("%s", e)
        return 2
    except RuntimeError as e:
        logger.error("%s", e)
        return 3


if __name__ == "__main__":
    sys.exit(main())
