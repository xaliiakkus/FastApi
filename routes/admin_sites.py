"""
Admin CRUD for bonus panel sites.
Mounted at /api/admin
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

import models
import storage
from routes.auth import require_admin

# Tum /admin endpoint'leri JWT + admin yetkisi ister
router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


def _require_site(site_id: int) -> dict:
    data = storage.load_site(site_id)
    if data is None:
        raise HTTPException(404, f"Site {site_id} not found")
    return data


# ─── Sites ────────────────────────────────────────────────────────────────────

@router.get("/sites")
def admin_list_sites() -> list[int]:
    return storage.list_sites()


@router.post("/sites", status_code=201)
def admin_create_site(body: models.SiteConfig) -> dict:
    if storage.load_site(body.id) is not None:
        raise HTTPException(409, f"Site {body.id} already exists")
    site_doc: dict[str, Any] = {
        "site": body.model_dump(),
        "categories": [],
        "texts": {"header": [], "footer": []},
        "popups": {"popup1": [], "popup2": []},
    }
    storage.save_site(body.id, site_doc)
    return site_doc


@router.get("/sites/{site_id}")
def admin_get_site(site_id: int) -> dict:
    return _require_site(site_id)


@router.patch("/sites/{site_id}")
def admin_update_site(site_id: int, body: models.SiteConfigUpdate) -> dict:
    doc = _require_site(site_id)
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    doc.setdefault("site", {"id": site_id}).update(patch)
    storage.save_site(site_id, doc)
    return doc["site"]


@router.delete("/sites/{site_id}", status_code=204)
def admin_delete_site(site_id: int) -> Response:
    _require_site(site_id)
    storage.delete_site(site_id)
    return Response(status_code=204)


# ─── Categories ───────────────────────────────────────────────────────────────

@router.get("/sites/{site_id}/categories")
def admin_list_cats(site_id: int) -> list:
    return storage.get_categories(_require_site(site_id))


@router.post("/sites/{site_id}/categories", status_code=201)
def admin_create_cat(site_id: int, body: models.CategoryCreate) -> dict:
    doc = _require_site(site_id)
    cat = storage.add_category(doc, body.model_dump())
    storage.save_site(site_id, doc)
    return cat


@router.patch("/sites/{site_id}/categories/{cat_id}")
def admin_update_cat(site_id: int, cat_id: int, body: models.CategoryCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.update_category(doc, cat_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(404, "Category not found")
    storage.save_site(site_id, doc)
    return result


@router.delete("/sites/{site_id}/categories/{cat_id}", status_code=204)
def admin_delete_cat(site_id: int, cat_id: int) -> Response:
    doc = _require_site(site_id)
    if not storage.delete_category(doc, cat_id):
        raise HTTPException(404, "Category not found")
    storage.save_site(site_id, doc)
    return Response(status_code=204)


# ─── Boards ───────────────────────────────────────────────────────────────────

@router.get("/sites/{site_id}/categories/{cat_id}/boards")
def admin_list_boards(site_id: int, cat_id: int) -> list:
    doc = _require_site(site_id)
    cat = storage.get_category(doc, cat_id)
    if cat is None:
        raise HTTPException(404, "Category not found")
    return cat.get("boards", [])


@router.post("/sites/{site_id}/categories/{cat_id}/boards", status_code=201)
def admin_create_board(site_id: int, cat_id: int, body: models.BoardCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.add_board(doc, cat_id, body.model_dump())
    if result is None:
        raise HTTPException(404, "Category not found")
    storage.save_site(site_id, doc)
    return result


@router.patch("/sites/{site_id}/boards/{board_id}")
def admin_update_board(site_id: int, board_id: int, body: models.BoardCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.update_board(doc, board_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(404, "Board not found")
    storage.save_site(site_id, doc)
    return result


@router.delete("/sites/{site_id}/boards/{board_id}", status_code=204)
def admin_delete_board(site_id: int, board_id: int) -> Response:
    doc = _require_site(site_id)
    if not storage.delete_board(doc, board_id):
        raise HTTPException(404, "Board not found")
    storage.save_site(site_id, doc)
    return Response(status_code=204)


# ─── Texts ────────────────────────────────────────────────────────────────────

@router.get("/sites/{site_id}/texts")
def admin_list_texts(site_id: int) -> dict:
    doc = _require_site(site_id)
    return doc.get("texts", {"header": [], "footer": []})


@router.post("/sites/{site_id}/texts", status_code=201)
def admin_create_text(site_id: int, body: models.TextItemCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.add_text(doc, body.model_dump())
    storage.save_site(site_id, doc)
    return result


@router.patch("/sites/{site_id}/texts/{text_id}")
def admin_update_text(site_id: int, text_id: int, body: models.TextItemCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.update_text(doc, text_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(404, "Text item not found")
    storage.save_site(site_id, doc)
    return result


@router.delete("/sites/{site_id}/texts/{text_id}", status_code=204)
def admin_delete_text(site_id: int, text_id: int) -> Response:
    doc = _require_site(site_id)
    if not storage.delete_text(doc, text_id):
        raise HTTPException(404, "Text item not found")
    storage.save_site(site_id, doc)
    return Response(status_code=204)


# ─── Popups ───────────────────────────────────────────────────────────────────

@router.get("/sites/{site_id}/popups/{popup_key}")
def admin_list_popups(site_id: int, popup_key: str) -> list:
    if popup_key not in ("popup1", "popup2"):
        raise HTTPException(400, "popup_key must be popup1 or popup2")
    return storage.get_popups(_require_site(site_id), popup_key)


@router.post("/sites/{site_id}/popups/{popup_key}", status_code=201)
def admin_create_popup(site_id: int, popup_key: str, body: models.PopupItemCreate) -> dict:
    if popup_key not in ("popup1", "popup2"):
        raise HTTPException(400, "popup_key must be popup1 or popup2")
    doc = _require_site(site_id)
    result = storage.add_popup(doc, popup_key, body.model_dump())
    storage.save_site(site_id, doc)
    return result


@router.patch("/sites/{site_id}/popups/{popup_id}")
def admin_update_popup(site_id: int, popup_id: int, body: models.PopupItemCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.update_popup(doc, popup_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(404, "Popup item not found")
    storage.save_site(site_id, doc)
    return result


@router.delete("/sites/{site_id}/popups/{popup_id}", status_code=204)
def admin_delete_popup(site_id: int, popup_id: int) -> Response:
    doc = _require_site(site_id)
    if not storage.delete_popup(doc, popup_id):
        raise HTTPException(404, "Popup item not found")
    storage.save_site(site_id, doc)
    return Response(status_code=204)


# ─── Banners ──────────────────────────────────────────────────────────────────

@router.get("/sites/{site_id}/banners")
def admin_list_banners(site_id: int) -> list:
    return storage.get_banners(_require_site(site_id))


@router.post("/sites/{site_id}/banners", status_code=201)
def admin_create_banner(site_id: int, body: models.BannerItemCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.add_banner(doc, body.model_dump())
    storage.save_site(site_id, doc)
    return result


@router.patch("/sites/{site_id}/banners/{banner_id}")
def admin_update_banner(site_id: int, banner_id: int, body: models.BannerItemCreate) -> dict:
    doc = _require_site(site_id)
    result = storage.update_banner(doc, banner_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(404, "Banner not found")
    storage.save_site(site_id, doc)
    return result


@router.delete("/sites/{site_id}/banners/{banner_id}", status_code=204)
def admin_delete_banner(site_id: int, banner_id: int) -> Response:
    doc = _require_site(site_id)
    if not storage.delete_banner(doc, banner_id):
        raise HTTPException(404, "Banner not found")
    storage.save_site(site_id, doc)
    return Response(status_code=204)
