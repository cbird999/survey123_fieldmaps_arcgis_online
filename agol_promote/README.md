# ArcGIS Online: config-driven promotion (linear)

Promote **hosted feature services**, **web maps**, and other configured items between environment folders in the **same** ArcGIS Online organization (e.g. `VegQC_DEV` → `VegQC_CERT` → `VegQC_TEST` → `VegQC_PROD`).

## Configuration: `projects.yaml`

- **`promotion_chain`**: ordered list of environment names. **Linear rule:** each run may only go **one step** forward (e.g. `DEV→CERT`, `CERT→TEST`, `TEST→PROD`). Use `--allow-nonlinear` only for emergencies.
- **`projects`**: map of project slug → `title_prefix`, `folder_pattern`, and `items`.

**Item title pattern:** `{title_prefix}_{ENV}{title_suffix}`  
Example: prefix `VegQC`, env `DEV`, suffix `_FL` → `VegQC_DEV_FL`.

**Folder pattern:** default `{prefix}_{env}` → e.g. `VegQC_DEV`.

**`items`:** list of `feature_service` and `web_map` entries. List **all `feature_service` rows before `web_map`** for stable cloning.

Add a new program by copying a block under `projects:` and changing `title_prefix` / suffixes as needed.

## CLI: `promote.py`

```bash
cd agol_promote
pip install -r requirements.txt

# Preview (no changes)
python promote.py --project vegqc --from DEV --to CERT --dry-run

# Promote one linear step
python promote.py --project vegqc --from DEV --to CERT

# Refresh target folder (deletes same-named target items, then clones)
python promote.py --project vegqc --from CERT --to TEST --replace
```

### Flags

| Flag | Purpose |
|------|--------|
| `--config path` | Alternate `projects.yaml` |
| `--content-owner USER` | Folder owner if not the signed-in account |
| `--no-copy-data` | Schema-only clone when Esri supports it for your items |
| `--search-existing-items` | Let `clone_items` reuse existing matches (default off) |
| `--allow-nonlinear` | Skip adjacent-env check (emergency) |

### Authentication

Same as before: `AGOL_PROFILE` / `--profile`, or `AGOL_CLIENT_ID`+`AGOL_REFRESH_TOKEN`, or `AGOL_USERNAME`+`AGOL_PASSWORD`, optional `AGOL_URL`.

### Legacy wrapper

`promote_dev_to_cert.py` runs `promote.py --project vegqc --from DEV --to CERT` plus any extra flags you pass.

## GitHub Actions

Workflow: **Actions → AGOL promote → Run workflow**.

1. In the repo, create **GitHub Environments** (Settings → Environments):
   - **`agol-promote`**: used for runs where `to_env` is not `PROD` (e.g. CERT, TEST).
   - **`agol-prod`**: used when `to_env` is `PROD` — add **required reviewers** here.

2. Add secrets to those environments (or organization secrets), e.g.:
   - `AGOL_CLIENT_ID`, `AGOL_REFRESH_TOKEN`
   - Optional `AGOL_URL` if not `https://www.arcgis.com`

3. The workflow defaults **`dry_run: true`** so the first run is safe; uncheck **dry_run** when you want a real clone.

**Triggering TEST then PROD:** run the workflow twice with matching hops, for example:

- `project=vegqc`, `from_env=DEV`, `to_env=CERT` (then CERT→TEST, then TEST→PROD).

Each run performs **exactly one** promotion step unless you use `--allow-nonlinear`.

## After promotion

- Set **sharing** / groups on new items.
- Point **Field Maps** / **Survey123** at the correct environment URLs/item IDs.
