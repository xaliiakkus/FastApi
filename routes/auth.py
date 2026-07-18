import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from db.db_setup import get_users_collection
from metrics_store import metrics_store

router = APIRouter()

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "Tr4ff1cBuddy_Pr0_L1c3ns3_H31md4l_2024!",
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "168"))
FREE_TRIAL_MINUTES = int(os.getenv("FREE_TRIAL_MINUTES", "30"))

# is_admin alani olmayan eski kayitlar icin env uzerinden admin listesi
ADMIN_USERNAMES = {
    name.strip()
    for name in os.getenv("ADMIN_USERNAMES", "heimdal").split(",")
    if name.strip()
}

_bearer_scheme = HTTPBearer(auto_error=False)


class LoginData(BaseModel):
    username: str
    password: str


class RegisterData(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(32).hex()
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return salt, password_hash


def verify_password(password: str, password_salt: str, password_hash: str) -> bool:
    _, computed_hash = hash_password(password, password_salt)
    return hmac.compare_digest(computed_hash, password_hash)


def _base64url_encode(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_token(user: dict) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    now = time.time()
    payload = {
        "sub": str(user.get("_id", "")),
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "license_type": user.get("license_type", "free"),
        "iat": int(now),
        "exp": int(now + JWT_EXPIRY_HOURS * 3600),
        "chk": hashlib.sha256(
            f"{user.get('username', '')}{user.get('license_type', 'free')}{JWT_SECRET}".encode()
        ).hexdigest()[:16],
    }

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")))
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return f"{message}.{_base64url_encode(signature)}"


def _base64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def decode_token(token: str) -> dict:
    """TrafficBuddy client ile ayni JWT formatini dogrular (imza + exp + chk)."""
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token")

    header_b64, payload_b64, signature_b64 = parts
    message = f"{header_b64}.{payload_b64}"
    expected_sig = hmac.new(
        JWT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(signature_b64, _base64url_encode(expected_sig)):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    try:
        payload = json.loads(_base64url_decode(payload_b64))
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if payload.get("exp", 0) < time.time():
        raise HTTPException(status_code=401, detail="Token expired")

    expected_chk = hashlib.sha256(
        f"{payload.get('username', '')}{payload.get('license_type', 'free')}{JWT_SECRET}".encode()
    ).hexdigest()[:16]
    if payload.get("chk") != expected_chk:
        raise HTTPException(status_code=401, detail="Token integrity check failed")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """Bearer token'i dogrular ve kullaniciyi DB'den taze halde dondurur."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    user = get_users_collection().find_one({"username": payload.get("username")})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.get("is_banned"):
        raise HTTPException(status_code=403, detail="Account is banned")
    if user.get("is_active") is False:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("is_admin") is True or user.get("username") in ADMIN_USERNAMES:
        return user
    raise HTTPException(status_code=403, detail="Admin access required")


def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "license_type": user.get("license_type"),
        "license_expiry": user.get("license_expiry"),
        "visit_credit": user.get("visit_credit"),
        "send_count": user.get("send_count"),
        "is_active": user.get("is_active"),
        "is_banned": user.get("is_banned"),
        "login_count": user.get("login_count"),
        "last_login": user.get("last_login"),
        "created_at": user.get("created_at"),
    }


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/login", tags=["auth"])
def login(data: LoginData, request: Request):
    users = get_users_collection()
    user = users.find_one(
        {
            "$or": [
                {"username": data.username},
                {"email": data.username},
            ]
        }
    )

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
        user.get("password_salt", ""),
        user.get("password_hash", ""),
    ):
        metrics_store.record_login(False)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    now = datetime.utcnow()
    client_ip = get_client_ip(request)

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


@router.get("/me", tags=["auth"])
def me(user: dict = Depends(get_current_user)):
    """Token gecerliyse guncel kullanici bilgisini dondurur."""
    return serialize_user(user)


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

    password_salt, password_hash = hash_password(data.password)
    now = datetime.utcnow()
    client_ip = get_client_ip(request)

    user_doc = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "password_salt": password_salt,
        "license_type": "free",
        "license_expiry": now + timedelta(minutes=FREE_TRIAL_MINUTES),
        "created_at": now,
        "last_login": None,
        "login_count": 0,
        "is_active": True,
        "is_banned": False,
        "ban_reason": None,
        "hwid": None,
        "last_ip": client_ip,
        "reg_ip": client_ip,
        "send_count": 2,
        "visit_credit": 200,
    }

    result = users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    return {
        "token": create_token(user_doc),
        "user": serialize_user(user_doc),
    }
