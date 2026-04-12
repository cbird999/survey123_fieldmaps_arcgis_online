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

    prof = profile or os.environ.get("AGOL_PROFILE")
    if prof:
        logger.info("Connecting with ArcGIS profile: %s", prof)
        return GIS(profile=prof)

    cid = os.environ.get("AGOL_CLIENT_ID")
    rt = os.environ.get("AGOL_REFRESH_TOKEN")
    if cid and rt:
        logger.info("Connecting with OAuth (client_id + refresh_token)")
        return GIS(url, client_id=cid, refresh_token=rt)

    user = os.environ.get("AGOL_USERNAME")
    pw = os.environ.get("AGOL_PASSWORD")
    if user and pw is not None:
        logger.info("Connecting as named user: %s", user)
        return GIS(url, user, pw)

    raise ValueError(
        "No credentials: set AGOL_PROFILE, or AGOL_CLIENT_ID+AGOL_REFRESH_TOKEN, "
        "or AGOL_USERNAME+AGOL_PASSWORD (optional: --profile, AGOL_URL)."
    )


def _folder_titles(user: Any) -> set[str]:
    folders = user.folders or []
    return {f.get("title") for f in folders if f.get("title")}


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
        return list(user.items(folder=folder, max_items=2000))
    except Exception as ex:
        logger.debug("Could not list folder %r: %s", folder, ex)
        return []


def _find_item_in_folder(user: Any, folder: str, title: str) -> Any:
    for item in _list_folder_items(user, folder):
        if item.title == title:
            return item
    raise LookupError(
        f"No item titled {title!r} in folder {folder!r} (owner {user.username!r})."
    )


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

    gis = _connect_gis(profile, url)
    me = gis.users.me
    logger.info("Signed in as %s", me.username)
    owner = content_owner or me.username
    if content_owner:
        logger.info("Content owner: %s", owner)

    user = gis.users.get(owner)

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
        _find_item_in_folder(user, src_folder, t) for t in source_titles
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
