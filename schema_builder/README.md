# vegqc-schema-builder

Small Python package that builds **file geodatabase** feature classes from declarative specs. Intended to run under **ArcGIS Pro** (for `arcpy`).

## Layout

| Path | Role |
|------|------|
| `vegqc_schema/builder.py` | Create GDB, coded domains, feature classes from dict specs |
| `vegqc_schema/vegetation.py` | Example: vegetation monitoring point / line / polygon classes |
| `vegqc_schema/registry.py` | Maps `--schema` names to `(domains, feature_classes)` |
| `vegqc_schema/__main__.py` | CLI |

## Setup

Use the Python environment shipped with ArcGIS Pro, then install in editable mode:

```bash
cd schema_builder
pip install -e .
```

## Usage

List layers defined by the vegetation example:

```bash
python -m vegqc_schema --list
```

Build all example classes into the default GDB (`schema_builder/VegMon_Schema.gdb`):

```bash
python -m vegqc_schema
```

Custom GDB and spatial reference:

```bash
python -m vegqc_schema --gdb C:\work\VegMon_DEV.gdb --wkid 2227
```

Build only selected feature classes:

```bash
python -m vegqc_schema --layers VegMon_SamplePoint VegMon_CorridorLine
```

Replace existing feature classes (keep GDB and domains):

```bash
python -m vegqc_schema --overwrite-layers
```

Recreate the entire GDB:

```bash
python -m vegqc_schema --overwrite-gdb
```

## Adding a new program schema

1. Add a module (e.g. `vegqc_schema/inspections.py`) exporting `DOMAINS` and `FEATURE_CLASSES` in the same shapes as `vegetation.py`.
2. Register it in `vegqc_schema/registry.py` under `SCHEMAS`.
