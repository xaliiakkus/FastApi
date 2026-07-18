import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Request, Response

from db.db_setup import get_client
from routes.auth import require_admin

router = APIRouter()

CLICK_LOG_DB = os.getenv("CLICK_LOG_DB", "bonus_panel")
CLICK_LOG_COLLECTION = os.getenv("CLICK_LOG_COLLECTION", "click_log")


def get_click_log_collection():
    return get_client()[CLICK_LOG_DB][CLICK_LOG_COLLECTION]


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip
    return request.client.host if request.client else None


@router.post("/click-log", tags=["clicks"])
async def create_click_log(request: Request) -> Response:
    """Sitelerden gelen dış link tıklamalarını bonus_panel.click_log'a yazar."""
    try:
        raw = await request.body()
        data = json.loads(raw.decode("utf-8")) if raw else {}
        if not isinstance(data, dict):
            data = {"payload": data}
    except (ValueError, UnicodeDecodeError):
        data = {}

    doc = {
        "site_id": data.get("site_id"),
        "site_host": data.get("site_host"),
        "page": data.get("page"),
        "url": data.get("url"),
        "firma": data.get("firma"),
        "link_text": data.get("link_text"),
        "referrer": data.get("referrer"),
        "client_ts": data.get("ts"),
        "ip": client_ip(request),
        "user_agent": request.headers.get("user-agent"),
        "created_at": datetime.now(timezone.utc),
    }

    try:
        get_click_log_collection().insert_one(doc)
    except Exception:
        # Loglama hatası kullanıcı akışını bozmamalı
        pass

    return Response(status_code=204)


@router.get("/click-log", tags=["clicks"], dependencies=[Depends(require_admin)])
def list_click_logs(
    days: int = Query(default=7, ge=1, le=90),
    site_id: int | None = Query(default=None),
    firma: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """Son tıklamaları listeler (admin panel)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    match: dict = {"created_at": {"$gte": since}}
    if site_id is not None:
        match["site_id"] = site_id
    if firma:
        match["firma"] = firma

    collection = get_click_log_collection()
    total = collection.count_documents(match)
    cursor = (
        collection.find(match, {"_id": 0})
        .sort("created_at", -1)
        .skip(offset)
        .limit(limit)
    )
    items = []
    for doc in cursor:
        created = doc.get("created_at")
        if hasattr(created, "isoformat"):
            doc["created_at"] = created.isoformat()
        items.append(doc)

    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/click-log/stats", tags=["clicks"], dependencies=[Depends(require_admin)])
def click_log_stats(days: int = Query(default=7, ge=1, le=90)) -> dict:
    """Son N gündeki tıklamaları firma ve site bazında özetler."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    match = {"created_at": {"$gte": since}}
    collection = get_click_log_collection()

    by_firma = list(
        collection.aggregate(
            [
                {"$match": match},
                {"$group": {"_id": "$firma", "clicks": {"$sum": 1}}},
                {"$sort": {"clicks": -1}},
            ]
        )
    )
    by_site = list(
        collection.aggregate(
            [
                {"$match": match},
                {"$group": {"_id": "$site_id", "clicks": {"$sum": 1}}},
                {"$sort": {"clicks": -1}},
            ]
        )
    )
    total = collection.count_documents(match)

    return {
        "days": days,
        "total": total,
        "by_firma": [{"firma": row["_id"], "clicks": row["clicks"]} for row in by_firma],
        "by_site": [{"site_id": row["_id"], "clicks": row["clicks"]} for row in by_site],
    }
