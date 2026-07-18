import os
import time
from pathlib import Path

# .env, diger moduller import edilmeden once yuklenmeli (env import aninda okunuyor)
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.db_setup import ping_mongodb
from metrics_store import metrics_store
from routes.admin_sites import router as admin_sites_router
from routes.auth import router as auth_router
from routes.click_log import router as click_log_router
from routes.metrics import router as metrics_router
from routes.sites import VITE_ASSETS, router as sites_router

app = FastAPI(title="Bonus Panel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(click_log_router, prefix="/api")
app.include_router(sites_router, prefix="/api")
app.include_router(admin_sites_router, prefix="/api/admin")

if VITE_ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(VITE_ASSETS)), name="assets")


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    client_ip = request.client.host if request.client else None
    query = str(request.url.query) if request.url.query else None

    metrics_store.record_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_ip=client_ip,
        query=query,
    )
    return response


@app.get("/")
def root():
    return {
        "service": "bonus-panel-api",
        "docs": "/docs",
        "register": "/api/register",
        "login": "/api/login",
        "metrics": "/api/metrics",
        "logs": "/api/logs",
        "click_log": "/api/click-log",
        "click_stats": "/api/click-log/stats",
        "site_data": "/api/site-data?site_id=1",
        "data_php": "/api/data.php?site_id=1",
        "admin_sites": "/api/admin/sites",
        "vite_assets": str(VITE_ASSETS),
        "vite_assets_mounted": VITE_ASSETS.exists(),
    }


@app.get("/health")
def health():
    mongo_status = "connected"
    try:
        ping_mongodb()
    except Exception as exc:
        mongo_status = str(exc)
    return {
        "status": "ok",
        "mongodb": mongo_status,
        "vite_assets": VITE_ASSETS.exists(),
    }
