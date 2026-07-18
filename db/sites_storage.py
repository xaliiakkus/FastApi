"""
MongoDB storage layer for bonus_panel sites.

Each site is stored as a single document in the `sites` collection:
  {
    "_id":        <site_id: int> | ObjectId
    "site":       { ... },
    "categories": [ ... ],
    "texts":      { "header": [...], "footer": [...] },
    "popups":     { "popup1": [...], "popup2": [...] },
    "big":        [ ... ]
  }

Environment variables
---------------------
  MONGODB_URI / MONGO_URL / DATABASE_URL  Shared via db.db_setup
  BONUS_PANEL_DB                          Database name (default: bonus_panel)
  SITES_COLLECTION                        Collection name (default: sites)

Initial seed
------------
If the collection is empty on first connect, JSON files under data/sites/
are imported automatically (one-time migration from file storage).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pymongo.collection import Collection

from db.db_setup import get_client

BONUS_PANEL_DB = os.getenv("BONUS_PANEL_DB", "bonus_panel")
SITES_COLLECTION = os.getenv("SITES_COLLECTION", "sites")
BUNDLE_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sites"

_seeded = False


def _col() -> Collection:
    """Return the `sites` collection; seed once if empty."""
    global _seeded
    col: Collection = get_client()[BONUS_PANEL_DB][SITES_COLLECTION]
    if not _seeded:
        _seed(col)
        _seeded = True
    return col


def _seed(col: Collection) -> None:
    """Import bundled JSON files into MongoDB if the collection is empty."""
    if col.count_documents({}, limit=1) > 0:
        return
    if not BUNDLE_DATA_DIR.exists():
        return
    docs = []
    for f in BUNDLE_DATA_DIR.glob("*.json"):
        if f.stem.isdigit():
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_id"] = int(f.stem)
            docs.append(data)
    if docs:
        col.insert_many(docs)


def _site_id_filter(site_id: int) -> dict[str, Any]:
    """Match seeded docs (_id=int) or Compass/imports where _id is ObjectId but site.id is set."""
    return {"$or": [{"_id": site_id}, {"site.id": site_id}]}


def load_site(site_id: int) -> dict[str, Any] | None:
    doc = _col().find_one(_site_id_filter(site_id))
    if doc is None:
        return None
    doc.pop("_id", None)
    return doc


def save_site(site_id: int, data: dict[str, Any]) -> None:
    col = _col()
    existing = col.find_one(_site_id_filter(site_id))
    out = {**data}
    site = out.get("site")
    if isinstance(site, dict):
        out["site"] = {**site, "id": site_id}
    if existing is not None:
        _id = existing["_id"]
        out["_id"] = _id
        col.replace_one({"_id": _id}, out)
    else:
        out["_id"] = site_id
        col.replace_one({"_id": site_id}, out, upsert=True)


def list_sites() -> list[int]:
    ids: list[int] = []
    for doc in _col().find({}, {"_id": 1, "site.id": 1}):
        sid = doc.get("_id")
        if isinstance(sid, int):
            ids.append(sid)
        else:
            raw = (doc.get("site") or {}).get("id")
            if raw is not None:
                ids.append(int(raw))
    return sorted(set(ids))


def delete_site(site_id: int) -> None:
    _col().delete_one(_site_id_filter(site_id))


# ─── helpers that work directly on the dict ──────────────────────────────────

def _next_id(items: list[dict]) -> int:
    return max((i.get("id", 0) for i in items), default=0) + 1


# categories
def get_categories(site: dict) -> list[dict]:
    return site.setdefault("categories", [])


def get_category(site: dict, cat_id: int) -> dict | None:
    return next((c for c in get_categories(site) if c["id"] == cat_id), None)


def add_category(site: dict, data: dict) -> dict:
    cats = get_categories(site)
    data["id"] = _next_id(cats)
    data.setdefault("boards", [])
    cats.append(data)
    return data


def update_category(site: dict, cat_id: int, data: dict) -> dict | None:
    cat = get_category(site, cat_id)
    if cat is None:
        return None
    data.pop("id", None)
    data.pop("boards", None)
    cat.update(data)
    return cat


def delete_category(site: dict, cat_id: int) -> bool:
    cats = get_categories(site)
    before = len(cats)
    site["categories"] = [c for c in cats if c["id"] != cat_id]
    return len(site["categories"]) < before


# boards
def _all_boards(site: dict) -> list[dict]:
    boards = []
    for cat in get_categories(site):
        boards.extend(cat.get("boards", []))
    return boards


def get_board(site: dict, board_id: int) -> dict | None:
    return next((b for b in _all_boards(site) if b["id"] == board_id), None)


def add_board(site: dict, cat_id: int, data: dict) -> dict | None:
    cat = get_category(site, cat_id)
    if cat is None:
        return None
    boards = cat.setdefault("boards", [])
    data["id"] = _next_id(_all_boards(site))
    data["catid"] = cat_id
    data["site_id"] = site["site"]["id"]
    boards.append(data)
    return data


def update_board(site: dict, board_id: int, data: dict) -> dict | None:
    board = get_board(site, board_id)
    if board is None:
        return None
    data.pop("id", None)
    board.update(data)
    return board


def delete_board(site: dict, board_id: int) -> bool:
    for cat in get_categories(site):
        before = len(cat.get("boards", []))
        cat["boards"] = [b for b in cat.get("boards", []) if b["id"] != board_id]
        if len(cat["boards"]) < before:
            return True
    return False


# text items
def get_texts(site: dict, tip: str) -> list[dict]:
    return site.setdefault("texts", {}).setdefault(tip, [])


def add_text(site: dict, data: dict) -> dict:
    tip = data.get("tip", "header")
    items = get_texts(site, tip)
    all_texts = get_texts(site, "header") + get_texts(site, "footer")
    data["id"] = _next_id(all_texts)
    items.append(data)
    return data


def update_text(site: dict, text_id: int, data: dict) -> dict | None:
    for tip in ("header", "footer"):
        for item in get_texts(site, tip):
            if item["id"] == text_id:
                data.pop("id", None)
                item.update(data)
                return item
    return None


def delete_text(site: dict, text_id: int) -> bool:
    for tip in ("header", "footer"):
        texts = get_texts(site, tip)
        before = len(texts)
        site["texts"][tip] = [t for t in texts if t["id"] != text_id]
        if len(site["texts"][tip]) < before:
            return True
    return False


# popup items
def get_popups(site: dict, popup_key: str) -> list[dict]:
    return site.setdefault("popups", {}).setdefault(popup_key, [])


def add_popup(site: dict, popup_key: str, data: dict) -> dict:
    items = get_popups(site, popup_key)
    all_p = get_popups(site, "popup1") + get_popups(site, "popup2")
    data["id"] = _next_id(all_p)
    items.append(data)
    return data


def update_popup(site: dict, popup_id: int, data: dict) -> dict | None:
    for key in ("popup1", "popup2"):
        for item in get_popups(site, key):
            if item["id"] == popup_id:
                data.pop("id", None)
                item.update(data)
                return item
    return None


def delete_popup(site: dict, popup_id: int) -> bool:
    for key in ("popup1", "popup2"):
        popups = get_popups(site, key)
        before = len(popups)
        site["popups"][key] = [p for p in popups if p["id"] != popup_id]
        if len(site["popups"][key]) < before:
            return True
    return False


# banners
def get_banners(site: dict) -> list[dict]:
    return site["site"].setdefault("banners", [])


def add_banner(site: dict, data: dict) -> dict:
    banners = get_banners(site)
    data["id"] = _next_id(banners)
    banners.append(data)
    return data


def update_banner(site: dict, banner_id: int, data: dict) -> dict | None:
    for b in get_banners(site):
        if b["id"] == banner_id:
            data.pop("id", None)
            b.update(data)
            return b
    return None


def delete_banner(site: dict, banner_id: int) -> bool:
    banners = get_banners(site)
    before = len(banners)
    site["site"]["banners"] = [b for b in banners if b["id"] != banner_id]
    return len(site["site"]["banners"]) < before


def build_big(site: dict) -> list[dict]:
    """Boards with slider == '2' (premium / big cards)."""
    if isinstance(site.get("big"), list) and site["big"]:
        return site["big"]
    return [b for b in _all_boards(site) if str(b.get("slider", "")) == "2"]
