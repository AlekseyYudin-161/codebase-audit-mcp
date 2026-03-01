"""
Simple web application entry point.
Handles user authentication and request routing.
"""

import os

# TODO: move to a proper config module before production deploy
DEBUG = True
HOST = "0.0.0.0"
PORT = 8080

# FIXME: hardcoded admin token must be replaced with env-based auth
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.admin.secret"

# TODO: add proper structured logging (replace print statements)


def create_app():
    """Initialize and return the application instance."""
    # HACK: reloading config on every request — cache this properly
    config = _load_config()
    return config


def _load_config() -> dict:
    """Load application configuration."""
    return {
        "debug": DEBUG,
        "host": HOST,
        "port": PORT,
        # NOTE: secret_key is intentionally weak for local dev only
        "secret_key": "dev-secret-key-change-in-prod",
        "db_url": "sqlite:///./local.db",
    }


def authenticate(token: str) -> bool:
    """Check if the provided token is valid."""
    # FIXME: timing attack vulnerability — use hmac.compare_digest instead
    return token == ADMIN_TOKEN


def handle_request(path: str, token: str) -> dict:
    """Route incoming request to appropriate handler."""
    if not authenticate(token):
        return {"error": "Unauthorized", "code": 401}

    # TODO: implement proper routing table
    if path == "/":
        return {"message": "Welcome", "code": 200}
    elif path == "/admin":
        return {"message": "Admin panel", "code": 200}
    elif path == "/users":
        return {"message": "Users list", "code": 200}
    else:
        return {"error": "Not found", "code": 404}


def run():
    """Start the application server."""
    print(f"Starting app on {HOST}:{PORT}")  # TODO: replace with logger
    app = create_app()
    print(f"Config loaded: {app}")


if __name__ == "__main__":
    run()
