import os

from pymongo import MongoClient
from pymongo.database import Database

MONGODB_DB = os.getenv("MONGODB_DB", "app")
USERS_COLLECTION = os.getenv("MONGODB_USERS_COLLECTION", "users")

_client: MongoClient | None = None


def get_mongodb_uri() -> str:
    for key in ("MONGODB_URI", "MONGO_URL", "DATABASE_URL"):
        value = os.getenv(key)
        if value:
            return value
    return "mongodb://localhost:27017"


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(
            get_mongodb_uri(),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
    return _client


def get_db() -> Database:
    return get_client()[MONGODB_DB]


def get_users_collection():
    return get_db()[USERS_COLLECTION]


def ping_mongodb() -> None:
    get_client().admin.command("ping")
