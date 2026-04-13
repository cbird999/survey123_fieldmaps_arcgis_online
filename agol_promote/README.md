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

**Duplicate titles in one folder:** After publishing from Pro, ArcGIS Online may list both **Service Definition** and **Feature Layer Collection** with the same title (e.g. `VegQC_DEV_FL`). The promoter picks **Feature Layer Collection** (or **Feature Service**) for `feature_service` items and skips the service definition.

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

Priority: **`AGOL_PROFILE`** / `--profile` → **`AGOL_USERNAME` + `AGOL_PASSWORD`** → **OAuth** (`AGOL_CLIENT_ID` + `AGOL_REFRESH_TOKEN` + optional `AGOL_CLIENT_SECRET`). Optional `AGOL_URL`.

Use **username/password** for a quick CI setup when the account has no MFA (or Esri allows app passwords—rare). SAML-only orgs may still need OAuth.

### Legacy wrapper

`promote_dev_to_cert.py` runs `promote.py --project vegqc --from DEV --to CERT` plus any extra flags you pass.

## Local testing (same as CI)

Use a **venv** with Python 3.9+ and install dependencies (no ArcGIS Pro required):

```bash
cd agol_promote
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set the **same variables** you use in GitHub (PowerShell example):

```powershell
cd agol_promote
.\.venv\Scripts\Activate.ps1

$env:AGOL_URL = "https://www.arcgis.com"   # or https://YOURORG.maps.arcgis.com
$env:AGOL_USERNAME = "<agol built-in username>"
$env:AGOL_PASSWORD = "<password>"
# Optional if not using password auth:
# $env:AGOL_CLIENT_ID / AGOL_CLIENT_SECRET / AGOL_REFRESH_TOKEN
$env:AGOL_CONTENT_OWNER = "cbird_gis"      # only if gis.users.me is None

# No changes to AGOL (recommended first)
python promote.py --project vegqc --from DEV --to CERT --dry-run -v

# Real promote (omit --dry-run)
# python promote.py --project vegqc --from DEV --to CERT
```

**Bash (macOS/Linux):**

```bash
cd agol_promote
source .venv/bin/activate
export AGOL_URL="https://www.arcgis.com"
export AGOL_USERNAME="..."
export AGOL_PASSWORD="..."
export AGOL_CONTENT_OWNER="cbird_gis"
python promote.py --project vegqc --from DEV --to CERT --dry-run -v
```

**Checks:**

- **`--dry-run -v`** should connect, list source items, and **not** clone.
- If local works but Actions fails, compare **env values** (especially `AGOL_URL`, `AGOL_CONTENT_OWNER`, and secrets pasted without extra newlines).

**No OAuth yet:** you can still validate config with `python promote.py --project vegqc --from DEV --to CERT --dry-run` only if `GIS(profile=...)` works via `AGOL_PROFILE` after signing in with ArcGIS Pro’s Python once, or use username/password where MFA allows it.

## GitHub Actions

Workflow: **Actions → AGOL promote → Run workflow**.

1. In the repo, create **GitHub Environments** (Settings → Environments):
   - **`agol-promote`**: used for runs where `to_env` is not `PROD` (e.g. CERT, TEST).
   - **`agol-prod`**: used when `to_env` is `PROD` — add **required reviewers** here.

2. Add **repository** secrets (recommended). **Auth order:** saved profile (not used in Actions) → **`AGOL_USERNAME` + `AGOL_PASSWORD`** if both set → else OAuth (`AGOL_CLIENT_ID` + `AGOL_REFRESH_TOKEN` + usually `AGOL_CLIENT_SECRET`).

   **Simplest CI path:** `AGOL_USERNAME`, `AGOL_PASSWORD` (built-in ArcGIS account; **MFA often breaks** this—use a non-MFA automation account if policy allows), plus optional `AGOL_URL`, `AGOL_CONTENT_OWNER`.

   **OAuth path:** `AGOL_CLIENT_ID`, `AGOL_REFRESH_TOKEN`, **`AGOL_CLIENT_SECRET`** (for many SAML/confidential apps), optional **`AGOL_CONTENT_OWNER`** if `gis.users.me` is `None`, optional `AGOL_URL`.

### CI / OAuth troubleshooting

If the workflow logs show **“paste the code”**, **SAML**, **Opening web browser**, or **`termios` / `getpass` errors**, the ArcGIS API fell back to **interactive** login. Fix:

1. Add secret **`AGOL_CLIENT_SECRET`** (same value as in your AGOL OAuth app).
2. Regenerate **`AGOL_REFRESH_TOKEN`** using the authorization-code flow (with `client_secret` in the token POST) so the token matches your app.
3. Ensure secret values have **no extra spaces or newlines** (re-paste if unsure).

Without **`client_secret`**, headless refresh often fails for confidential apps, and the library tries browser/SAML login, which **cannot** work on `ubuntu-latest`.

If you see **`gis.users.me is None`** / **`AttributeError: 'NoneType'... username`**:

- Set **`AGOL_URL`** to your **organization** host, e.g. `https://YOURORG.maps.arcgis.com` (not only `https://www.arcgis.com` for some orgs).
- Add **`AGOL_CONTENT_OWNER`** with the **ArcGIS username** of the account that owns the OAuth token (often `user@ORG` or `org_username`).
- Regenerate the refresh token using the **same** portal base URL you put in **`AGOL_URL`**.

4. The workflow defaults **`dry_run: true`** so the first run is safe; uncheck **dry_run** when you want a real clone.

**Triggering TEST then PROD:** run the workflow twice with matching hops, for example:

- `project=vegqc`, `from_env=DEV`, `to_env=CERT` (then CERT→TEST, then TEST→PROD).

Each run performs **exactly one** promotion step unless you use `--allow-nonlinear`.

## After promotion

- Set **sharing** / groups on new items.
- Point **Field Maps** / **Survey123** at the correct environment URLs/item IDs.
