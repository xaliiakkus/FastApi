import hashlib
import hmac
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from jose import jwt
from pydantic import BaseModel

from db.db_setup import get_users_collection
from metrics_store import metrics_store

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


class LoginData(BaseModel):
    username: str
    password: str


def verify_password(password: str, password_hash: str, password_salt: str) -> bool:
    data = (password_salt + password).encode("utf-8")
    computed = hashlib.sha256(data).hexdigest()
    return hmac.compare_digest(computed, password_hash)


def create_token(user: dict) -> str:
    payload = {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user.get("email"),
        "license_type": user.get("license_type"),
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "license_type": user.get("license_type"),
        "license_expiry": user.get("license_expiry"),
        "visit_credit": user.get("visit_credit"),
        "is_active": user.get("is_active"),
        "is_banned": user.get("is_banned"),
        "login_count": user.get("login_count"),
        "last_login": user.get("last_login"),
        "created_at": user.get("created_at"),
    }


@router.post("/login", tags=["auth"])
def login(data: LoginData, request: Request):
    users = get_users_collection()
    query = {
        "$or": [
            {"username": data.username},
            {"email": data.username},
        ]
    }
    user = users.find_one(query)

    if not user:
        metrics_store.record_login(False)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.get("is_banned"):
        metrics_store.record_login(False)
        raise HTTPException(status_code=403, detail="Account is banned")

    if user.get("is_active") is False:
        metrics_store.record_login(False)
        raise HTTPException(status_code=403, detail="Account is inactive")

    if not verify_password(
        data.password,
        user.get("password_hash", ""),
        user.get("password_salt", ""),
    ):
        metrics_store.record_login(False)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    now = datetime.utcnow()
    client_ip = request.client.host if request.client else None

    users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"last_login": now, "last_ip": client_ip},
            "$inc": {"login_count": 1},
        },
    )

    user["last_login"] = now
    user["login_count"] = user.get("login_count", 0) + 1
    if client_ip:
        user["last_ip"] = client_ip

    metrics_store.record_login(True)
    return {
        "token": create_token(user),
        "user": serialize_user(user),
    }
