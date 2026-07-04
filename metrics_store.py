import threading
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


MAX_LOGS = int(__import__("os").getenv("MAX_REQUEST_LOGS", "500"))


@dataclass
class RequestLog:
    timestamp: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    client_ip: str | None
    query: str | None = None


class MetricsStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.logs: deque[RequestLog] = deque(maxlen=MAX_LOGS)
        self.total_requests = 0
        self.status_counts: dict[str, int] = {}
        self.path_counts: dict[str, int] = {}
        self.method_counts: dict[str, int] = {}
        self.total_duration_ms = 0.0
        self.login_success = 0
        self.login_failed = 0
        self.started_at = datetime.now(timezone.utc)

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str | None,
        query: str | None = None,
    ) -> None:
        entry = RequestLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=client_ip,
            query=query,
        )
        with self._lock:
            self.logs.appendleft(entry)
            self.total_requests += 1
            self.total_duration_ms += duration_ms
            self.status_counts[str(status_code)] = self.status_counts.get(str(status_code), 0) + 1
            self.path_counts[path] = self.path_counts.get(path, 0) + 1
            self.method_counts[method] = self.method_counts.get(method, 0) + 1

    def record_login(self, success: bool) -> None:
        with self._lock:
            if success:
                self.login_success += 1
            else:
                self.login_failed += 1

    def get_metrics(self) -> dict:
        with self._lock:
            uptime_seconds = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            avg_duration = (
                round(self.total_duration_ms / self.total_requests, 2)
                if self.total_requests
                else 0.0
            )
            return {
                "started_at": self.started_at.isoformat(),
                "uptime_seconds": round(uptime_seconds, 1),
                "total_requests": self.total_requests,
                "avg_duration_ms": avg_duration,
                "status_counts": dict(self.status_counts),
                "path_counts": dict(self.path_counts),
                "method_counts": dict(self.method_counts),
                "login_success": self.login_success,
                "login_failed": self.login_failed,
                "stored_logs": len(self.logs),
                "max_stored_logs": MAX_LOGS,
            }

    def get_logs(self, limit: int = 100, offset: int = 0) -> dict:
        with self._lock:
            items = list(self.logs)
        sliced = items[offset : offset + limit]
        return {
            "total": len(items),
            "limit": limit,
            "offset": offset,
            "logs": [asdict(item) for item in sliced],
        }


metrics_store = MetricsStore()
