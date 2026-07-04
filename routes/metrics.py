import os

from fastapi import APIRouter, HTTPException, Query, Request

from metrics_store import metrics_store

router = APIRouter()

METRICS_API_KEY = os.getenv("METRICS_API_KEY")


def verify_metrics_access(request: Request) -> None:
    if not METRICS_API_KEY:
        return
    if request.headers.get("X-Metrics-Key") != METRICS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid metrics key")


@router.get("/metrics", tags=["monitoring"])
def get_metrics(request: Request):
    verify_metrics_access(request)
    return metrics_store.get_metrics()


@router.get("/logs", tags=["monitoring"])
def get_logs(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    verify_metrics_access(request)
    return metrics_store.get_logs(limit=limit, offset=offset)
