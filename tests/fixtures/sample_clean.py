# Test fixture: clean file with no issues.
# scan_todos must return 0 items.
# find_code_smells must return 0 items.

import hashlib
import os
from pathlib import Path


def read_config(config_path: Path) -> dict:
    """Read configuration from a JSON file safely."""
    if not config_path.exists():
        return {}
    text = config_path.read_text(encoding="utf-8")
    import json

    return json.loads(text)


def compute_checksum(data: bytes) -> str:
    """Compute SHA-256 checksum of data."""
    return hashlib.sha256(data).hexdigest()


def get_env_secret(key: str) -> str:
    """Read secret from environment variable, never from code."""
    value = os.environ.get(key, "")
    if not value:
        raise RuntimeError(f"Environment variable '{key}' is not set.")
    return value


def validate_age(age: int) -> bool:
    """Return True if age is in valid human range."""
    return 0 <= age <= 120


def format_greeting(name: str, age: int) -> str:
    """Return a simple greeting string."""
    return f"Hello, {name}! You are {age} years old."
