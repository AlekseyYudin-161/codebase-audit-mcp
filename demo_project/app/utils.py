"""
Utility functions for data processing and validation.
"""

from typing import Any

# NOTE: all thresholds below are magic numbers — move to config
MAX_RETRIES = 3
TIMEOUT = 30
CHUNK_SIZE = 256
RATE_LIMIT = 100


def validate_and_process_user_data(data: dict) -> dict:
    """
    Validate incoming user data and normalize it for storage.

    This function handles all validation, transformation and
    enrichment in one place.

    HACK: this should be split into separate validator and transformer classes.
    """
    # --- validation phase ---
    if not data:
        return {"error": "empty input"}
    if not isinstance(data, dict):
        return {"error": "input must be a dict"}
    if "username" not in data:
        return {"error": "missing username"}
    if not isinstance(data["username"], str):
        return {"error": "username must be string"}
    if len(data["username"]) < 3:
        return {"error": "username too short"}
    if len(data["username"]) > 50:
        return {"error": "username too long"}
    if "email" not in data:
        return {"error": "missing email"}
    if "@" not in data.get("email", ""):
        return {"error": "invalid email"}
    if "." not in data.get("email", "").split("@")[-1]:
        return {"error": "invalid email domain"}
    if "age" not in data:
        return {"error": "missing age"}
    if not isinstance(data["age"], int):
        return {"error": "age must be integer"}
    if data["age"] < 0:
        return {"error": "age cannot be negative"}
    if data["age"] > 150:
        return {"error": "unrealistic age"}
    if "role" not in data:
        return {"error": "missing role"}
    if data["role"] not in ("admin", "user", "guest", "moderator"):
        return {"error": "unknown role"}

    # --- transformation phase ---
    username = data["username"].strip().lower()
    email = data["email"].strip().lower()
    age = int(data["age"])
    role = data["role"]

    # TODO: add phone number validation
    phone = data.get("phone", "").strip()

    # TODO: add address validation
    address = data.get("address", "").strip()

    # --- enrichment phase ---
    permissions = []
    if role == "admin":
        permissions = ["read", "write", "delete", "manage_users"]
    elif role == "moderator":
        permissions = ["read", "write", "delete"]
    elif role == "user":
        permissions = ["read", "write"]
    else:
        permissions = ["read"]

    # FIXME: avatar URL not validated for SSRF
    avatar_url = data.get("avatar_url", f"https://avatars.example.com/{username}")

    return {
        "username": username,
        "email": email,
        "age": age,
        "role": role,
        "phone": phone,
        "address": address,
        "permissions": permissions,
        "avatar_url": avatar_url,
        "verified": False,
        "active": True,
    }


def retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES) -> Any:
    """Retry a function call with exponential backoff."""
    import time

    last_error = None
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            last_error = e
            wait = 2**attempt
            # NOTE: blocking sleep — consider async version
            time.sleep(wait)
    raise RuntimeError(f"Failed after {max_retries} retries: {last_error}")


def chunk_list(items: list, size: int = CHUNK_SIZE) -> list:
    """Split a list into chunks of given size."""
    # TODO: use generator for memory efficiency on large lists
    return [items[i : i + size] for i in range(0, len(items), size)]


# DEPRECATED: use validate_and_process_user_data instead
def old_validate_user(data: dict) -> bool:
    """Legacy user validation — kept for backward compatibility."""
    # XXX: this does not validate email or role
    return bool(data.get("username") and data.get("email"))
