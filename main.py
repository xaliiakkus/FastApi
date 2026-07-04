import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from db.db_setup import ping_mongodb
from metrics_store import metrics_store
from routes.auth import router as auth_router
from routes.metrics import router as metrics_router

app = FastAPI(title="Login API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")


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
        "service": "login-api",
        "docs": "/docs",
        "register": "/api/register",
        "login": "/api/login",
        "metrics": "/api/metrics",
        "logs": "/api/logs",
    }


@app.get("/health")
def health():
    mongo_status = "connected"
    try:
        ping_mongodb()
    except Exception as exc:
        mongo_status = str(exc)
    return {"status": "ok", "mongodb": mongo_status}
