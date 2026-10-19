"""
auth_controller.py
------------------
Business-logic layer for user authentication.
Sits between the auth views and the user model.
"""

import re
from app.models import user_model


# ── Validation helpers ────────────────────────────────────────────────────────

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_PATTERN_NUM = re.compile(r"\d")
PASSWORD_PATTERN_SYM = re.compile(r'[!@#$%^&*(),.?":{}|<>]')


def validate_email(email: str) -> str | None:
    """Return an error string, or None if valid."""
    if not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."
    return None


def validate_password_strength(password: str) -> str | None:
    """Return an error string, or None if password meets requirements."""
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not PASSWORD_PATTERN_NUM.search(password):
        return "Password must contain at least one number."
    if not PASSWORD_PATTERN_SYM.search(password):
        return "Password must contain at least one special character."
    return None


# ── Login ─────────────────────────────────────────────────────────────────────

def login(email: str, password: str) -> tuple[bool, str]:
    """
    Attempt to log in.
    Returns (success: bool, message: str).
    """
    if not email or not password:
        return False, "Please fill in all fields."

    err = validate_email(email)
    if err:
        return False, err

    user = user_model.find_user_by_email(email)
    if user and user_model.verify_password(password, user["password"]):
        user_model.update_last_login(email)
        return True, "Login Successful!"

    return False, "Invalid Email or Password."


# ── Register ──────────────────────────────────────────────────────────────────

def register(
    full_name: str, email: str, password: str, confirm_password: str
) -> tuple[bool, str]:
    """
    Attempt to register a new user.
    Returns (success: bool, message: str).
    """
    if not all([full_name, email, password, confirm_password]):
        return False, "Please fill all fields."

    err = validate_email(email)
    if err:
        return False, err

    if password != confirm_password:
        return False, "Passwords do not match."

    err = validate_password_strength(password)
    if err:
        return False, err

    if user_model.email_exists(email):
        return False, "Email already registered."

    try:
        user_model.register_user(full_name, email, password)
        return True, "Registration Successful! You can now login."
    except Exception as exc:
        return False, f"Registration failed: {exc}"


# ── Forgot / Change Password ──────────────────────────────────────────────────

def request_password_reset(email: str) -> tuple[bool, str]:
    """
    Check if the email exists and acknowledge the reset request.
    (In production, this would send an email.)
    """
    if not email:
        return False, "Please enter your email."

    if not user_model.email_exists(email):
        return False, "Email not found in our records."

    return (
        True,
        "If your email is registered, you will receive password reset instructions shortly.",
    )


def change_password(
    email: str, current_password: str, new_password: str, confirm_password: str
) -> tuple[bool, str]:
    """
    Change an authenticated user's password.
    Returns (success: bool, message: str).
    """
    if not all([current_password, new_password, confirm_password]):
        return False, "All fields are required."

    if new_password != confirm_password:
        return False, "New password and confirm password do not match."

    err = validate_password_strength(new_password)
    if err:
        return False, err

    user = user_model.find_user_by_email(email)
    if not user or not user_model.verify_password(current_password, user["password"]):
        return False, "Current password is incorrect."

    user_model.update_password(email, new_password)
    return True, "Password changed successfully."
