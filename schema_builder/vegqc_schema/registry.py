"""Register schema modules here so the CLI can target them with --schema."""

from __future__ import annotations

from typing import Any

from vegqc_schema.vegetation import DOMAINS as VEGETATION_DOMAINS
from vegqc_schema.vegetation import FEATURE_CLASSES as VEGETATION_FEATURE_CLASSES

SchemaEntry = tuple[list[dict[str, Any]], list[dict[str, Any]]]

SCHEMAS: dict[str, SchemaEntry] = {
    "vegetation": (VEGETATION_DOMAINS, VEGETATION_FEATURE_CLASSES),
}


def resolve_schema(name: str) -> SchemaEntry:
    if name not in SCHEMAS:
        choices = ", ".join(sorted(SCHEMAS))
        raise KeyError(f"Unknown schema {name!r}. Choose one of: {choices}")
    return SCHEMAS[name]
