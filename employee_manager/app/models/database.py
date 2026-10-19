"""
database.py
-----------
Centralized MongoDB connection management.
Loads DB_URL from the .env file via python-dotenv.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_client() -> MongoClient:
    """Return a MongoClient using the DB_URL from environment variables."""
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL is not set in the .env file.")
    return MongoClient(db_url)


# ── Singleton-style shared client ────────────────────────────────────────────
_client: MongoClient | None = None


def get_shared_client() -> MongoClient:
    """Return (and lazily create) the shared MongoClient instance."""
    global _client
    if _client is None:
        _client = get_client()
    return _client


def get_auth_db():
    """Return the authentication database."""
    return get_shared_client()["user_auth_db"]


def get_employee_db():
    """Return the employee management database."""
    return get_shared_client()["employee_management"]


def get_users_collection():
    """Return the Email_users collection."""
    return get_auth_db()["Email_users"]


def get_employees_collection():
    """Return the employees collection."""
    return get_employee_db()["employees"]
