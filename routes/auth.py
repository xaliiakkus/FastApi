import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from jose import jwt
from pydantic import BaseModel, EmailStr, Field

from db.db_setup import get_users_collection
from metrics_store import metrics_store

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


class LoginData(BaseModel):
    username: str
    password: str


class RegisterData(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


def hash_password(password: str) -> tuple[str, str]:
    password_salt = secrets.token_hex(32)
    password_hash = hashlib.sha256((password_salt + password).encode("utf-8")).hexdigest()
    return password_hash, password_salt


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


@router.post("/register", tags=["auth"])
def register(data: RegisterData, request: Request):
    users = get_users_collection()
    username = data.username.strip()
    email = str(data.email).strip().lower()

    existing = users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing:
        if existing.get("username") == username:
            raise HTTPException(status_code=409, detail="Username already exists")
        raise HTTPException(status_code=409, detail="Email already exists")

    password_hash, password_salt = hash_password(data.password)
    now = datetime.utcnow()
    client_ip = request.client.host if request.client else None

    user_doc = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "password_salt": password_salt,
        "license_type": "free",
        "license_expiry": None,
        "created_at": now,
        "last_login": None,
        "login_count": 0,
        "is_active": True,
        "visit_credit": 0,
        "is_banned": False,
        "hwid": None,
        "last_ip": None,
        "reg_ip": client_ip,
    }

    result = users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    return {
        "token": create_token(user_doc),
        "user": serialize_user(user_doc),
    }
