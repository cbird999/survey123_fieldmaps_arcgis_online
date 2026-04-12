"""Create file GDB domains and feature classes from declarative specs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _require_arcpy():
    try:
        import arcpy  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "arcpy is required. Run this package using ArcGIS Pro's Python "
            "(e.g. activate the arcgispro-py3 conda environment)."
        ) from e
    return arcpy


def ensure_file_gdb(gdb_path: Path, overwrite: bool = False) -> Path:
    """Create a file geodatabase at gdb_path if it does not exist."""
    arcpy = _require_arcpy()
    gdb_path = gdb_path.resolve()
    parent = gdb_path.parent
    name = gdb_path.stem  # foo.gdb -> foo

    if gdb_path.exists():
        if not gdb_path.is_dir() or not str(gdb_path).lower().endswith(".gdb"):
            raise FileExistsError(f"Path exists and is not a file GDB: {gdb_path}")
        if overwrite:
            arcpy.management.Delete(str(gdb_path))
        else:
            return gdb_path

    parent.mkdir(parents=True, exist_ok=True)
    arcpy.management.CreateFileGDB(str(parent), name)
    logger.info("Created file GDB: %s", gdb_path)
    return gdb_path


def _create_coded_domain(arcpy: Any, gdb: str, spec: dict[str, Any]) -> None:
    name = spec["name"]
    desc = spec.get("description", name)
    field_type = spec.get("field_type", "TEXT")
    arcpy.management.CreateDomain(gdb, name, desc, field_type, "CODED")
    for code, label in spec["coded_values"]:
        arcpy.management.AddCodedValueToDomain(gdb, name, code, label)
    logger.info("Domain created: %s", name)


def _domain_names(arcpy: Any, gdb: str) -> set[str]:
    """ArcGIS Pro returns a dict name -> domain object; older APIs may return a list."""
    raw = arcpy.da.ListDomains(gdb)
    if not raw:
        return set()
    if isinstance(raw, dict):
        return set(raw.keys())
    return set(raw)


def build_domains(gdb: str | Path, domain_specs: list[dict[str, Any]]) -> None:
    """Create coded-value domains in the workspace (skipped if domain exists)."""
    arcpy = _require_arcpy()
    gdb = str(Path(gdb).resolve())
    existing = _domain_names(arcpy, gdb)
    for spec in domain_specs:
        name = spec["name"]
        if name in existing:
            logger.debug("Domain already exists, skipping: %s", name)
            continue
        _create_coded_domain(arcpy, gdb, spec)


def _add_field(arcpy: Any, fc: str, field: dict[str, Any]) -> None:
    name = field["name"]
    ftype = field["type"]
    alias = field.get("alias", "")
    length = field.get("length")
    nullable = field.get("nullable", True)
    kwargs: dict[str, Any] = {
        "field_is_nullable": "NULLABLE" if nullable else "NON_NULLABLE",
    }
    if alias:
        kwargs["field_alias"] = alias
    if ftype == "TEXT" and length:
        arcpy.management.AddField(fc, name, ftype, field_length=length, **kwargs)
    else:
        arcpy.management.AddField(fc, name, ftype, **kwargs)


def build_feature_class(
    gdb: str | Path,
    spec: dict[str, Any],
    spatial_reference_wkid: int,
    overwrite: bool = False,
) -> str:
    """
    Create one feature class from a spec dict:
      name, geometry (POINT | POLYLINE | POLYGON), fields (list of field dicts).
    Returns the full catalog path to the feature class.
    """
    arcpy = _require_arcpy()
    gdb = str(Path(gdb).resolve())
    name = spec["name"]
    geometry = spec["geometry"]
    fields: list[dict[str, Any]] = spec.get("fields", [])
    fc = str(Path(gdb) / name)

    if arcpy.Exists(fc):
        if overwrite:
            arcpy.management.Delete(fc)
        else:
            raise FileExistsError(
                f"Feature class already exists: {fc}. Use overwrite=True to replace."
            )

    sr = arcpy.SpatialReference(spatial_reference_wkid)
    arcpy.management.CreateFeatureclass(
        gdb,
        name,
        geometry,
        spatial_reference=sr,
    )
    logger.info("Created feature class: %s (%s)", name, geometry)

    for field in fields:
        _add_field(arcpy, fc, field)

    for field in fields:
        domain = field.get("domain")
        if domain:
            arcpy.management.AssignDomainToField(fc, field["name"], domain)

    return fc


def build_all(
    gdb: Path,
    domain_specs: list[dict[str, Any]],
    feature_class_specs: list[dict[str, Any]],
    spatial_reference_wkid: int,
    overwrite: bool = False,
) -> list[str]:
    """Create GDB if needed, domains, then all feature classes."""
    ensure_file_gdb(gdb, overwrite=overwrite)
    gdb_str = str(gdb.resolve())
    build_domains(gdb_str, domain_specs)
    created: list[str] = []
    for spec in feature_class_specs:
        created.append(
            build_feature_class(
                gdb_str,
                spec,
                spatial_reference_wkid=spatial_reference_wkid,
                overwrite=overwrite,
            )
        )
    return created
