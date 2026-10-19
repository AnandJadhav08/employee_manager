"""
user_model.py
-------------
Data-access layer for user authentication records.
All MongoDB interactions for the Email_users collection live here.
"""

import datetime
import bcrypt
from app.models.database import get_users_collection


def _col():
    return get_users_collection()


# ── QUERIES ───────────────────────────────────────────────────────────────────

def find_user_by_email(email: str) -> dict | None:
    return _col().find_one({"email": email})


def email_exists(email: str) -> bool:
    return _col().find_one({"email": email}) is not None


# ── AUTHENTICATION ────────────────────────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def hash_password(plain_password: str) -> bytes:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())


# ── CRUD ──────────────────────────────────────────────────────────────────────

def register_user(full_name: str, email: str, plain_password: str) -> bool:
    """Create a new user account. Returns True on success."""
    hashed = hash_password(plain_password)
    _col().insert_one(
        {
            "full_name": full_name,
            "email": email,
            "password": hashed,
            "created_at": datetime.datetime.now(),
            "last_login": None,
        }
    )
    return True


def update_last_login(email: str) -> None:
    _col().update_one(
        {"email": email},
        {"$set": {"last_login": datetime.datetime.now()}},
    )


def update_password(email: str, new_plain_password: str) -> bool:
    """Update the password for the given email. Returns True on success."""
    hashed = hash_password(new_plain_password)
    result = _col().update_one(
        {"email": email},
        {"$set": {"password": hashed}},
    )
    return result.modified_count > 0
