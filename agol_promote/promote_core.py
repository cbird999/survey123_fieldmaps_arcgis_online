"""Load projects.yaml, validate linear promotion, run ArcGIS Online clone."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("agol_promote")

VALID_KINDS = frozenset({"feature_service", "web_map"})


@dataclass(frozen=True)
class ItemSpec:
    kind: str
    title_suffix: str


@dataclass(frozen=True)
class ProjectSpec:
    slug: str
    title_prefix: str
    folder_pattern: str
    items: tuple[ItemSpec, ...]


def load_config(path: Path) -> tuple[list[str], dict[str, ProjectSpec]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not raw:
        raise ValueError(f"Empty config: {path}")

    chain = raw.get("promotion_chain")
    if not chain or not isinstance(chain, list):
        raise ValueError("projects.yaml: missing promotion_chain (list of env names)")
    chain_norm = [str(e).strip().upper() for e in chain]
    if len(chain_norm) != len(set(chain_norm)):
        raise ValueError("promotion_chain contains duplicate env names")

    projects_raw = raw.get("projects") or {}
    if not isinstance(projects_raw, dict):
        raise ValueError("projects.yaml: projects must be a mapping")

    projects: dict[str, ProjectSpec] = {}
    for slug, pdata in projects_raw.items():
        slug = str(slug).strip().lower()
        if not slug:
            continue
        prefix = (pdata.get("title_prefix") or "").strip()
        if not prefix:
            raise ValueError(f"Project {slug!r}: title_prefix required")
        folder_pat = (pdata.get("folder_pattern") or "{prefix}_{env}").strip()
        items_raw = pdata.get("items") or []
        if not items_raw:
            raise ValueError(f"Project {slug!r}: at least one item required")
        specs: list[ItemSpec] = []
        for i, it in enumerate(items_raw):
            kind = str(it.get("kind", "")).strip().lower()
            if kind not in VALID_KINDS:
                raise ValueError(f"Project {slug!r} item {i}: kind must be feature_service or web_map")
            suf = str(it.get("title_suffix", "")).strip()
            if not suf:
                raise ValueError(f"Project {slug!r} item {i}: title_suffix required")
            specs.append(ItemSpec(kind=kind, title_suffix=suf))
        projects[slug] = ProjectSpec(
            slug=slug,
            title_prefix=prefix,
            folder_pattern=folder_pat,
            items=tuple(specs),
        )

    return chain_norm, projects


def normalize_env(name: str) -> str:
    return str(name).strip().upper()


def assert_linear_promotion(chain: list[str], from_env: str, to_env: str) -> None:
    fe = normalize_env(from_env)
    te = normalize_env(to_env)
    if fe not in chain:
        raise ValueError(f"Unknown source env {fe!r}; chain is {chain}")
    if te not in chain:
        raise ValueError(f"Unknown target env {te!r}; chain is {chain}")
    i = chain.index(fe)
    j = chain.index(te)
    if j != i + 1:
        nxt = chain[i + 1] if i + 1 < len(chain) else None
        raise ValueError(
            f"Linear promotion only: {fe} → {te} is not allowed. "
            f"After {fe}, the next stage is {nxt!r}."
        )


def folder_name(project: ProjectSpec, env: str) -> str:
    e = normalize_env(env)
    return project.folder_pattern.format(prefix=project.title_prefix, env=e)


def item_title(project: ProjectSpec, env: str, spec: ItemSpec) -> str:
    e = normalize_env(env)
    return f"{project.title_prefix}_{e}{spec.title_suffix}"


def specs_in_clone_order(items: tuple[ItemSpec, ...]) -> list[ItemSpec]:
    """feature_service first, then web_map; stable within each group."""
    fs = [s for s in items if s.kind == "feature_service"]
    wm = [s for s in items if s.kind == "web_map"]
    return fs + wm


def _connect_gis(profile: str | None, url: str) -> Any:
    import os

    from arcgis.gis import GIS

    url = (url or "").strip() or "https://www.arcgis.com"

    prof = (profile or os.environ.get("AGOL_PROFILE") or "").strip() or None
    if prof:
        logger.info("Connecting with ArcGIS profile: %s", prof)
        return GIS(profile=prof)

    cid = (os.environ.get("AGOL_CLIENT_ID") or "").strip()
    rt = (os.environ.get("AGOL_REFRESH_TOKEN") or "").strip()
    csec = (os.environ.get("AGOL_CLIENT_SECRET") or "").strip() or None

    if cid and rt:
        logger.info("Connecting with OAuth (client_id + refresh_token)")
        if os.environ.get("GITHUB_ACTIONS") == "true" and not csec:
            logger.warning(
                "AGOL_CLIENT_SECRET is not set. SAML / confidential OAuth apps often need it "
                "for non-interactive token refresh in CI; without it the API may fall back to "
                "browser login (which fails on GitHub runners). Add secret AGOL_CLIENT_SECRET."
            )
        gis_kw: dict[str, Any] = {"client_id": cid, "refresh_token": rt}
        if csec:
            gis_kw["client_secret"] = csec
            logger.info("Using client_secret for OAuth token exchange")
        return GIS(url, **gis_kw)

    user = (os.environ.get("AGOL_USERNAME") or "").strip()
    pw = os.environ.get("AGOL_PASSWORD")
    if pw is not None:
        pw = pw.strip()
    if user and pw is not None and pw != "":
        logger.info("Connecting as named user: %s", user)
        return GIS(url, user, pw)

    raise ValueError(
        "No credentials: set AGOL_PROFILE, or AGOL_CLIENT_ID+AGOL_REFRESH_TOKEN "
        "(and usually AGOL_CLIENT_SECRET for CI), "
        "or AGOL_USERNAME+AGOL_PASSWORD (optional: --profile, AGOL_URL)."
    )


def _username_from_portal_properties(gis: Any) -> str | None:
    """Fallback when gis.users.me is None (org URL / OAuth timing / API version quirks)."""
    import json

    try:
        p = gis.properties
    except Exception as ex:
        logger.debug("gis.properties failed: %s", ex)
        return None
    try:
        user = p.get("user") if hasattr(p, "get") else getattr(p, "user", None)
        if user is None:
            return None
        if isinstance(user, str):
            obj = json.loads(user)
            return obj.get("username") if isinstance(obj, dict) else None
        if isinstance(user, dict):
            return user.get("username")
        return getattr(user, "username", None)
    except Exception as ex:
        logger.debug("Could not parse user from portal properties: %s", ex)
        return None


def _resolve_owner_username(gis: Any, content_owner: str | None) -> str:
    import os

    if content_owner and str(content_owner).strip():
        return str(content_owner).strip()

    me = None
    try:
        me = gis.users.me
    except Exception as ex:
        logger.debug("gis.users.me raised: %s", ex)
    if me is not None:
        return me.username

    from_props = _username_from_portal_properties(gis)
    if from_props:
        logger.info("Resolved username from portal properties: %s", from_props)
        return from_props

    env_owner = (os.environ.get("AGOL_CONTENT_OWNER") or "").strip()
    if env_owner:
        logger.warning(
            "gis.users.me is None; using AGOL_CONTENT_OWNER=%s",
            env_owner,
        )
        return env_owner

    raise RuntimeError(
        "Cannot determine ArcGIS username: gis.users.me is None. "
        "Fix: (1) Set secret AGOL_URL to your org root, e.g. https://YOURORG.maps.arcgis.com "
        "(many SAML orgs need this instead of https://www.arcgis.com). "
        "(2) Add repository secret AGOL_CONTENT_OWNER with the promoting user's username. "
        "(3) Regenerate AGOL_REFRESH_TOKEN using the same portal URL as AGOL_URL. "
        "Or pass --content-owner USER on the CLI."
    )


def _folder_entry_title(entry: Any) -> str | None:
    """ArcGIS API may return dicts or Folder objects for user.folders."""
    if entry is None:
        return None
    if isinstance(entry, dict):
        t = entry.get("title")
        return str(t).strip() if t else None
    t = getattr(entry, "title", None)
    return str(t).strip() if t else None


def _folder_titles(user: Any) -> set[str]:
    if user is None:
        return set()
    folders = user.folders or []
    return {t for f in folders if (t := _folder_entry_title(f))}


def _ensure_folder(gis: Any, owner_username: str, folder_name_str: str, dry_run: bool) -> None:
    user = gis.users.get(owner_username)
    if folder_name_str in _folder_titles(user):
        return
    if dry_run:
        logger.info("[dry-run] Would create folder: %s", folder_name_str)
        return
    logger.info("Creating folder: %s", folder_name_str)
    gis.content.create_folder(folder_name_str, owner=owner_username)


def _list_folder_items(user: Any, folder: str) -> list[Any]:
    try:
        return list(user.items(folder=folder, max_items=5000))
    except Exception as ex:
        logger.debug("Could not list folder %r: %s", folder, ex)
        return []


def _item_type(it: Any) -> str:
    return str(it.type or "")


def _candidates_same_title(items: list[Any], title: str) -> tuple[list[Any], bool]:
    """Return items matching title (exact first); bool True if case-insensitive fallback used."""
    exact = [i for i in items if i.title == title]
    if exact:
        return exact, False
    loose = [i for i in items if i.title.lower() == title.lower()]
    if loose:
        logger.warning(
            "Matched title case-insensitively: expected %r; types=%s",
            title,
            [_item_type(i) for i in loose],
        )
        return loose, True
    return [], False


def _pick_item_for_spec_kind(candidates: list[Any], item_kind: str, title: str) -> Any | None:
    """
    Same AGOL title is often used for Service Definition + Feature Layer Collection after publishing.
    Promote the hosted layer item, not the .sd companion.
    """
    if not candidates:
        return None
    if item_kind == "web_map":
        for it in candidates:
            if _item_type(it) == "Web Map":
                return it
        return None
    if item_kind == "feature_service":
        skip_types = {
            "Service Definition",
            "File Geodatabase",
            "Shapefile",
            "CSV",
            "Microsoft Excel",
        }
        usable = [it for it in candidates if _item_type(it) not in skip_types]
        for preferred in ("Feature Layer Collection", "Feature Service"):
            for it in usable:
                if _item_type(it) == preferred:
                    if len(candidates) > 1:
                        logger.info(
                            "Selected %r for clone: type=%s id=%s (same title also on other item types)",
                            title,
                            _item_type(it),
                            it.id,
                        )
                    return it
        for it in usable:
            if _is_feature_service_item(it):
                return it
        return None
    return candidates[0]


def _find_item_in_folder(
    user: Any,
    folder: str,
    title: str,
    *,
    item_kind: str,
    gis: Any | None = None,
    owner_username: str | None = None,
) -> Any:
    items = _list_folder_items(user, folder)
    titles_found = sorted({i.title for i in items})

    candidates, _ = _candidates_same_title(items, title)
    chosen = _pick_item_for_spec_kind(candidates, item_kind, title)
    if chosen is not None:
        return chosen
    if candidates:
        raise LookupError(
            f"No suitable {item_kind!r} item titled {title!r} in folder {folder!r} "
            f"(owner {user.username!r}). Same title exists with types: "
            f"{[_item_type(i) for i in candidates]}. "
            "Expected e.g. Feature Layer Collection for feature_service, Web Map for web_map."
        )

    if gis is not None and owner_username:
        try:
            q = f"title:{title} owner:{owner_username}"
            searched = list(gis.content.search(query=q, max_items=100))
        except Exception as ex:
            logger.debug("content.search fallback failed: %s", ex)
            searched = []
        search_cands = [
            it
            for it in searched
            if (it.title == title or it.title.lower() == title.lower())
            and (
                (o := getattr(it, "owner", None)) == owner_username
                or (o and o.lower() == owner_username.lower())
            )
        ]
        chosen = _pick_item_for_spec_kind(search_cands, item_kind, title)
        if chosen is not None:
            logger.warning(
                "Found %r via content.search (folder listing missed or order differed); id=%s type=%s",
                title,
                chosen.id,
                _item_type(chosen),
            )
            return chosen

    hint = (
        f"No item titled {title!r} in folder {folder!r} (owner {user.username!r}). "
        f"Found {len(titles_found)} item(s) in that folder"
    )
    if titles_found:
        preview = titles_found[:50]
        hint += f" with title(s): {preview}"
        if len(titles_found) > 50:
            hint += " ..."
    else:
        hint += (
            " (folder empty or not visible with this token). "
            "Confirm AGOL_CONTENT_OWNER is the item owner username, "
            "the service account can see that user’s content, and items are in that folder."
        )
    raise LookupError(hint)


def _is_feature_service_item(item: Any) -> bool:
    t = (item.type or "").lower()
    if t == "web map":
        return False
    return (
        "feature service" in t
        or t == "feature layer collection"
        or (t == "feature layer" and "hosted" in (item.typeKeywords or []))
    )


def _normalize_clone_result(result: Any) -> list[Any]:
    if result is None:
        return []
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        out: list[Any] = []
        for v in result.values():
            if isinstance(v, list):
                out.extend(v)
            else:
                out.append(v)
        return out
    return [result]


def _delete_targets_if_replace(
    user: Any,
    target_folder: str,
    target_titles: list[str],
    dry_run: bool,
) -> None:
    titles_set = set(target_titles)
    for item in _list_folder_items(user, target_folder):
        if item.title in titles_set:
            if dry_run:
                logger.info("[dry-run] Would delete existing: %s (%s)", item.title, item.id)
            else:
                logger.warning("Deleting existing target item: %s (%s)", item.title, item.id)
                item.delete()


def _apply_target_names_and_tags(
    cloned_items: list[Any],
    source_items: list[Any],
    target_titles: list[str],
    from_env: str,
    to_env: str,
    dry_run: bool,
) -> None:
    fe = normalize_env(from_env)
    te = normalize_env(to_env)
    extra_tags = [f"env:{te.lower()}", f"promoted-from:{fe.lower()}"]

    if dry_run:
        for src, tgt_title in zip(source_items, target_titles):
            base_tags = list(src.tags or [])
            merged = ", ".join(sorted({*base_tags, *extra_tags}))
            logger.info(
                "[dry-run] Would rename clone -> title=%r type=%s tags=%s",
                tgt_title,
                src.type,
                merged,
            )
        return

    fss = [i for i in cloned_items if _is_feature_service_item(i)]
    wms = [i for i in cloned_items if (i.type or "") == "Web Map"]

    fi = wi = 0
    matched: list[Any] = []
    for src, tgt_title in zip(source_items, target_titles):
        if _is_feature_service_item(src):
            if fi >= len(fss):
                raise RuntimeError("Clone output missing a feature service for each source feature service")
            new_item = fss[fi]
            fi += 1
        elif (src.type or "") == "Web Map":
            if wi >= len(wms):
                raise RuntimeError("Clone output missing a web map for each source web map")
            new_item = wms[wi]
            wi += 1
        else:
            raise RuntimeError(f"Unsupported source item type for promotion: {src.type!r}")

        base_tags = list(src.tags or [])
        merged = ", ".join(sorted({*base_tags, *extra_tags}))
        new_item.update(item_properties={"title": tgt_title, "tags": merged})
        logger.info("Updated: %s (%s) -> title %r", new_item.type, new_item.id, tgt_title)
        matched.append(new_item)

    if fi != len(fss) or wi != len(wms):
        raise RuntimeError(
            f"Clone produced unused clones: expected fs={fi}/{len(fss)} wm={wi}/{len(wms)}; "
            "adjust projects.yaml or extend pairing logic."
        )

    matched_set = set(id(x) for x in matched)
    for i in cloned_items:
        if id(i) not in matched_set:
            logger.warning("Unmatched cloned item (not renamed): type=%r title=%r id=%s", i.type, i.title, i.id)


def run_promotion(
    *,
    config_path: Path,
    project_slug: str,
    from_env: str,
    to_env: str,
    url: str,
    profile: str | None,
    content_owner: str | None,
    replace: bool,
    dry_run: bool,
    copy_data: bool,
    search_existing_items: bool,
    allow_nonlinear: bool,
) -> None:
    chain, projects = load_config(config_path)
    slug = project_slug.strip().lower()
    if slug not in projects:
        choices = ", ".join(sorted(projects))
        raise ValueError(f"Unknown project {slug!r}. Configured projects: {choices}")

    fe = normalize_env(from_env)
    te = normalize_env(to_env)
    if allow_nonlinear:
        if fe not in chain or te not in chain:
            raise ValueError(
                f"Unknown env in nonlinear mode: {fe!r} or {te!r} not in chain {chain}"
            )
        logger.warning("Nonlinear promotion allowed: %s -> %s (override)", fe, te)
    else:
        assert_linear_promotion(chain, fe, te)

    project = projects[slug]
    ordered_specs = specs_in_clone_order(project.items)
    src_folder = folder_name(project, fe)
    tgt_folder = folder_name(project, te)

    source_titles = [item_title(project, fe, s) for s in ordered_specs]
    target_titles = [item_title(project, te, s) for s in ordered_specs]

    url = (url or "").strip() or "https://www.arcgis.com"
    gis = _connect_gis(profile, url)
    owner = _resolve_owner_username(gis, content_owner)
    logger.info("Using content owner (folder/items user): %s", owner)

    user = gis.users.get(owner)
    if user is None:
        raise ValueError(
            f"No ArcGIS user found for {owner!r}. "
            "Fix AGOL_CONTENT_OWNER (or --content-owner) to match an existing member username exactly."
        )

    _ensure_folder(gis, owner, tgt_folder, dry_run)

    if replace:
        _delete_targets_if_replace(user, tgt_folder, target_titles, dry_run)

    if not dry_run:
        existing = {i.title for i in _list_folder_items(user, tgt_folder)}
        overlap = [t for t in target_titles if t in existing]
        if overlap and not replace:
            raise ValueError(
                f"Target folder {tgt_folder!r} already has: {overlap}. Use --replace or remove items."
            )

    source_items = [
        _find_item_in_folder(
            user,
            src_folder,
            item_title(project, fe, spec),
            item_kind=spec.kind,
            gis=gis,
            owner_username=owner,
        )
        for spec in ordered_specs
    ]
    for it, tit in zip(source_items, source_titles):
        logger.info("Source: %r (%s) type=%s", tit, it.id, it.type)

    if dry_run:
        logger.info(
            "[dry-run] Would clone %s items %s -> folder %r owner=%s",
            len(source_items),
            [i.id for i in source_items],
            tgt_folder,
            owner,
        )
        _apply_target_names_and_tags(
            [],
            source_items,
            target_titles,
            fe,
            te,
            dry_run=True,
        )
        return

    clone_kw: dict[str, Any] = {
        "items": source_items,
        "owner": owner,
        "folder": tgt_folder,
        "copy_data": copy_data,
        "search_existing_items": search_existing_items,
    }
    logger.info("Cloning...")
    raw = gis.content.clone_items(**clone_kw)
    cloned = _normalize_clone_result(raw)
    logger.info("Clone returned %s item(s)", len(cloned))
    for it in cloned:
        logger.info("  Cloned: %s (%s) type=%s", it.title, it.id, it.type)

    _apply_target_names_and_tags(cloned, source_items, target_titles, fe, te, dry_run=False)
    logger.info("Done (%s -> %s for project %s). Check sharing/groups in AGOL.", fe, te, slug)
